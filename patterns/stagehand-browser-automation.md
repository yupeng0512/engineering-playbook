---
title: stagehand-browser-automation
type: note
permalink: engineering-playbook/patterns/stagehand-browser-automation
---

# Stagehand 浏览器自动化模式：代码 + AI 混合控制

> 来源: Stagehand 框架调研与实践 (https://github.com/browserbase/stagehand)
> 沉淀时间: 2026-02-26

---

## 适用场景

- E2E 测试中页面频繁改版导致选择器失效
- 爬虫/数据采集需要解析复杂且多变的 DOM 结构
- RPA 内部工具自动化，不同账号看到不同 UI
- 多网站统一流程，无法为每个站点写单独的选择器
- 需要"能上线、能长期跑"的自动化方案

---

## 核心模式

### 模式 1: 确定性 + AI 混合（推荐）

**原则**：哪里确定用代码，哪里不确定交给 AI。

```typescript
const page = stagehand.context.pages()[0];

// 确定的部分：代码控制（零 LLM 成本、毫秒级执行）
await page.goto("https://internal-tool.company.com/login");
await page.waitForLoadState("domcontentloaded");

// 不确定的部分：AI 处理（UI 改了也不怕）
await stagehand.act("type %user% into the username field", {
  variables: { user: process.env.LOGIN_USER! },
});
await stagehand.act("click the login button");

// 确定的断言：代码校验
const url = page.url();
expect(url).toContain("/dashboard");

// 不确定的提取：AI 理解页面结构
const data = await stagehand.extract("Extract dashboard metrics",
  z.object({
    totalUsers: z.number(),
    activeToday: z.number(),
    revenue: z.string(),
  })
);
```

**决策表**：

| 操作类型 | 确定性高 → 代码 | 确定性低 → AI |
|---------|----------------|--------------|
| 导航 | `page.goto(url)` | - |
| 点击 | `page.click('#known-id')` | `stagehand.act("click the X button")` |
| 填写 | `page.fill('#email', value)` | `stagehand.act("type %val% into email field")` |
| 提取 | `page.textContent('.price')` | `stagehand.extract("extract price", z.number())` |
| 等待 | `page.waitForSelector()` | `stagehand.observe("check if loaded")` |
| 断言 | `expect(value).toBe(x)` | - (断言永远用代码) |

### 模式 2: 缓存驱动的渐进式确定化

首次运行用 AI 推理，后续复用缓存，兼具灵活性和性能。

```typescript
const stagehand = new Stagehand({
  env: "LOCAL",
  cacheDir: "cache/checkout-flow",
});

// 首次：AI 推理找到按钮 → 缓存 xpath
// 后续：直接用缓存的 xpath，不调 LLM
await stagehand.act("click the checkout button");

// 网站改版导致 xpath 失效 → 自动降级回 AI 推理 → 重新缓存
```

**缓存组织**：
```
cache/
├── login-flow/          # 按业务流程分目录
├── data-extraction/
└── checkout-flow/
```

**生产建议**：将 cache 目录提交到版本控制，CI/CD 首次不需要 LLM 推理。

### 模式 3: observe → act 安全执行

先观察后执行，避免 AI "乱点"。

```typescript
// 先看：获取候选操作列表
const [action] = await stagehand.observe("find the delete button");

// 再验证：确认是预期的操作
if (action && action.description.includes("Delete")) {
  // 最后执行：传入已验证的 action
  await stagehand.act(action);
}
```

### 模式 4: Playwright 工程 + Stagehand 增强

在成熟的 Playwright 测试套件中，逐步引入 Stagehand 增强脆弱的测试。

```typescript
import { test, expect } from "@playwright/test";
import { Stagehand } from "@browserbasehq/stagehand";

test("checkout flow with AI-enhanced resilience", async () => {
  const stagehand = new Stagehand({ env: "LOCAL", cacheDir: "cache/tests" });
  await stagehand.init();
  const page = stagehand.context.pages()[0];

  // Playwright 精确操作
  await page.goto("https://shop.example.com");

  // Stagehand AI 操作（UI 改版自愈）
  await stagehand.act("add the first product to cart");
  await stagehand.act("go to checkout");

  // AI 提取 + Playwright 断言
  const total = await stagehand.extract("extract the order total",
    z.number()
  );
  expect(total).toBeGreaterThan(0);

  await stagehand.close();
});
```

---

## 与纯 Playwright 对比

| 维度 | 纯 Playwright | Stagehand + Playwright 混合 |
|------|--------------|---------------------------|
| 选择器维护 | 高（页面改必修） | 低（AI 自适应） |
| 运行成本 | 零 LLM 费用 | 有 LLM 费用（可缓存降至接近零） |
| 执行速度 | 毫秒级 | 首次秒级，缓存后毫秒级 |
| 跨站适配 | 每站一套选择器 | 同一指令适配多站 |
| 数据提取 | 手写正则/CSS 选择器 | Schema 声明式，AI 自动解析 |
| 调试能力 | DevTools + Trace | DevTools + LLM 日志 + Browserbase 录制 |
| 学习曲线 | CSS/XPath 选择器 | 自然语言 + Zod Schema |
| 适合场景 | 稳定页面的回归测试 | 变化频繁页面的自动化 |

**结论**：不是替代关系，而是互补。Stagehand 增强 Playwright，在不确定性高的场景提供自愈能力。

---

## 成本控制策略

| 策略 | 节省效果 | 实现方式 |
|------|---------|---------|
| 确定性操作用代码 | 100% | `page.goto()`, `page.click()` |
| 启用 Action Caching | 90%+ | `cacheDir: "cache/xxx"` |
| Targeted Extract | 50%+ | `{ selector: "xpath=..." }` 缩小范围 |
| 选择经济型模型 | 80%+ | `gemini-2.5-flash` 替代 `gpt-5` |
| 批量操作合并 | 30%+ | 一次 extract 多个字段而非多次调用 |

---

## 常见踩坑

### 1. 不要让 AI 处理断言逻辑

```
❌ await stagehand.act("verify the price is $99.99")
✅ const price = await stagehand.extract("extract the price", z.number());
   expect(price).toBe(99.99);
```

断言必须用代码，AI 判断的"对不对"不可靠。

### 2. 不要一条指令做多步

```
❌ await stagehand.act("fill form and submit and wait for confirmation")
✅ await stagehand.act("fill the name field with 'John'");
   await stagehand.act("click submit");
   await page.waitForSelector('.confirmation');
```

### 3. extract Schema 的 describe 很关键

```typescript
// 没有 describe → AI 猜测字段含义，可能提取错误
z.object({ val: z.string() })

// 有 describe → AI 精准理解
z.object({ val: z.string().describe("the product SKU code like 'ABC-123'") })
```

### 4. headless 环境系统依赖

Linux 服务器无头运行需要：
```bash
apt-get install -y libnss3-dev libatk-bridge2.0-dev libgtk-3-dev libxss1 libasound2
```

---

## 前后对比

| 维度 | 无此 Pattern | 使用此 Pattern |
|------|-------------|---------------|
| 页面改版影响 | 选择器全部失效，脚本崩溃 | AI 自动适配新 DOM，继续运行 |
| 爬虫开发效率 | 手写正则+CSS 选择器，1-2 天/站 | Schema 声明+AI 提取，2-4 小时/站 |
| 测试维护成本 | 频繁修选择器，月均 20% 维护时间 | 缓存+自愈，月均 5% 维护时间 |
| 多站点适配 | 每站独立脚本 | 同一脚本适配多站 |
| LLM 运行成本 | N/A（但人力维护成本高） | 缓存后接近零（首次约 $0.01/次） |

---

## 注意事项

1. **断言永远用代码**，不要依赖 AI 判断正确性
2. **生产环境必须启用缓存**，否则每次运行都消耗 LLM token
3. **敏感数据用 variables 传递**，不会发送给 LLM 提供商
4. **Stagehand v3 底层基于 Playwright**，两者 API 可以无缝混用
5. **agent() 适合探索任务**，生产流程优先用 act+extract 的确定性组合
6. **多语言支持**：TypeScript (主), Python, Go, Java, Ruby SDK 均可用
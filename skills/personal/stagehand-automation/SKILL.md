---
name: stagehand-automation
description: Stagehand 浏览器自动化专家。当用户表达"浏览器自动化"、"AI 自动化测试"、"网页爬虫"、"数据提取"、"E2E 测试"、"Stagehand"、"自愈测试"、"自然语言操作浏览器"等意图时触发。帮助编写代码+AI混合控制的浏览器自动化脚本。
permalink: engineering-playbook/skills/personal/stagehand-automation/skill
---

# Stagehand 浏览器自动化专家

> 基于 Stagehand 框架，实现"代码精确控制 + AI 模糊理解"的混合浏览器自动化

---

## 核心理念

**哪里确定用代码，哪里不确定交给 AI。**

Stagehand 不是用 AI 取代代码，而是把 AI 当作"智能的显式函数"来调用。在同一个脚本中：
- 用 **Playwright/代码** 处理你已理解的、稳定的页面操作（导航、认证、精确断言）
- 用 **Stagehand AI** 处理不确定的、变化快的页面操作（模糊匹配、结构化提取、动态 UI 适配）

---

## 四大核心 API

### 1. `act()` - 自然语言动作执行

用自然语言描述要做的操作，AI 自动定位并执行。

```typescript
// 不再需要脆弱的选择器
await stagehand.act("click the login button");
await stagehand.act("type %username% into the email field", {
  variables: { username: "user@example.com" }
});
await stagehand.act("select 'Monthly' from the billing dropdown");
```

**最佳实践**：
- 单步操作，不要在一条指令里做多件事
- 提供上下文定位："click the red 'Delete' button next to John Smith"
- 敏感数据用 `variables` 传递（不会发送给 LLM）

### 2. `extract()` - 结构化数据提取

用 Zod Schema 定义数据结构，AI 自动从页面提取并清洗。

```typescript
import { z } from "zod";

const products = await stagehand.extract(
  "Extract all product listings",
  z.array(z.object({
    name: z.string().describe("product title"),
    price: z.number().describe("price in USD"),
    rating: z.number().optional().describe("star rating 1-5"),
  }))
);
```

**最佳实践**：
- 用 `.describe()` 为每个字段添加说明
- 价格等格式不统一的字段优先用 `z.string()`
- 大量数据分页提取，避免单次提取过多

### 3. `observe()` - 页面观察与推理

先"看一眼"页面，获取可用操作列表，再决定下一步。

```typescript
const actions = await stagehand.observe("find all navigation links");
// actions: [{ description: "Home", method: "click", selector: "..." }, ...]

// 观察后精确执行
const [loginBtn] = await stagehand.observe("find the login button");
if (loginBtn) {
  await stagehand.act(loginBtn); // 直接传入观察结果
}
```

**最佳实践**：
- 不确定页面状态时，先 observe 再 act
- 用 observe 做条件分支（页面上有什么决定做什么）

### 4. `agent()` - 多步骤自主代理

将复杂的多步任务交给 AI Agent 自主完成。

```typescript
const agent = stagehand.agent({
  mode: "cua",
  model: "google/gemini-2.5-computer-use-preview-10-2025",
  systemPrompt: "You are a helpful assistant that can control a web browser.",
});

const result = await agent.execute({
  instruction: "Find the latest PR and extract its title and author",
  maxSteps: 10,
});
```

**注意**：agent 适合探索性任务，生产环境优先用 act + extract 的确定性组合。

---

## 决策框架：何时用代码 vs AI

| 场景 | 推荐方式 | 原因 |
|------|---------|------|
| URL 导航 | `page.goto()` (代码) | 确定性操作，零成本 |
| 已知选择器点击 | `page.click()` (代码) | 稳定且高效 |
| 表单填写 | `act()` + variables | AI 定位 + 安全传值 |
| 页面结构频繁变化的按钮 | `act()` | AI 模糊匹配，自愈 |
| 复杂 DOM 数据提取 | `extract()` | 免写解析逻辑 |
| 动态内容判断 | `observe()` | 先看再做 |
| 多步骤探索任务 | `agent()` | 自主决策 |
| 断言/校验 | 代码 `expect()` | 精确可靠 |
| 登录认证流程 | 代码 + `act()` 混合 | 凭据代码管理，UI交互AI处理 |

---

## 环境配置

### 本地开发

```typescript
import { Stagehand } from "@browserbasehq/stagehand";

const stagehand = new Stagehand({
  env: "LOCAL",
  localBrowserLaunchOptions: {
    headless: false,
    args: ["--no-sandbox"],
  },
  cacheDir: "cache/my-workflow",
});
await stagehand.init();
```

### 生产部署（Browserbase 云）

```typescript
const stagehand = new Stagehand({
  env: "BROWSERBASE",
  cacheDir: "cache/production",
  browserbaseSessionCreateParams: {
    proxies: true,
    browserSettings: {
      blockAds: true,
      solveCaptchas: true,
    },
  },
});
await stagehand.init();
```

### 环境变量

```bash
# LLM Provider（至少配一个）
OPENAI_API_KEY=sk-xxx
# ANTHROPIC_API_KEY=sk-ant-xxx
# GOOGLE_GENERATIVE_AI_API_KEY=xxx

# Browserbase 云（生产可选）
# BROWSERBASE_API_KEY=xxx
# BROWSERBASE_PROJECT_ID=xxx
```

---

## 与 Playwright 集成

Stagehand 底层就是 Playwright，两者无缝混用：

```typescript
import { Stagehand } from "@browserbasehq/stagehand";
import { chromium } from "playwright-core";

const stagehand = new Stagehand({ env: "LOCAL" });
await stagehand.init();

// 通过 CDP 连接 Playwright
const browser = await chromium.connectOverCDP({
  wsEndpoint: stagehand.connectURL(),
});
const pwPage = browser.contexts()[0].pages()[0];

// Playwright 精确操作
await pwPage.goto("https://example.com");
await pwPage.waitForLoadState("domcontentloaded");

// Stagehand AI 操作（传入 Playwright page）
await stagehand.act("click the login button", { page: pwPage });
const data = await stagehand.extract("extract article titles", 
  z.array(z.string()), { page: pwPage });
```

---

## 缓存与成本优化

### Action Caching（关键特性）

```typescript
const stagehand = new Stagehand({
  env: "LOCAL",
  cacheDir: "cache/login-flow",
});

// 首次运行：调用 LLM 推理，结果缓存到本地
await stagehand.act("click the login button");

// 后续运行：直接复用缓存，不调用 LLM，速度和纯代码一样快
await stagehand.act("click the login button");
```

**缓存组织建议**：
```
cache/
├── login-flow/        # 登录流程
├── data-extraction/   # 数据提取
└── checkout-flow/     # 结账流程
```

### 成本控制策略

1. **确定性操作用代码**：`page.goto()`, `page.click('#known-id')` 零 LLM 成本
2. **启用缓存**：重复操作只调一次 LLM
3. **targeted extract**：用 `selector` 缩小提取范围，减少 token
4. **选择高性价比模型**：`gemini-2.5-flash` 比 `gpt-5` 便宜 10x+

---

## 自愈机制 (Self-Healing)

Stagehand 内置自愈能力：

1. 网站改版导致 `act()` 失败时，自动重新分析 DOM 寻找新路径
2. 配合 observe → act 模式，先确认元素存在再操作
3. 缓存的 action 失效时自动降级到 LLM 推理

```typescript
// 自愈模式最佳实践
try {
  await stagehand.act("click the submit button", { timeout: 10000 });
} catch (error) {
  // fallback: 用 observe 重新定位
  const [action] = await stagehand.observe("find the submit button");
  if (action) {
    await stagehand.act(action);
  }
}
```

---

## 实战模板

### 模板 1: 登录 + 数据提取

```typescript
import "dotenv/config";
import { Stagehand } from "@browserbasehq/stagehand";
import { z } from "zod";

async function scrapeWithLogin(url: string, credentials: { user: string; pass: string }) {
  const stagehand = new Stagehand({
    env: "LOCAL",
    cacheDir: "cache/scrape",
    localBrowserLaunchOptions: { headless: true, args: ["--no-sandbox"] },
  });
  await stagehand.init();
  const page = stagehand.context.pages()[0];

  // 代码：精确导航
  await page.goto(url);

  // AI：处理登录表单（不管 UI 怎么变）
  await stagehand.act("type %user% into the username field", {
    variables: { user: credentials.user },
  });
  await stagehand.act("type %pass% into the password field", {
    variables: { pass: credentials.pass },
  });
  await stagehand.act("click the login button");

  // 代码：等待页面加载
  await page.waitForLoadState("networkidle");

  // AI：结构化提取数据
  const data = await stagehand.extract(
    "Extract all items from the dashboard table",
    z.array(z.object({
      name: z.string(),
      status: z.string(),
      lastUpdated: z.string(),
    }))
  );

  await stagehand.close();
  return data;
}
```

### 模板 2: 多页面并发提取

```typescript
async function extractMultiplePages(urls: string[]) {
  const stagehand = new Stagehand({
    env: "LOCAL",
    cacheDir: "cache/multi-page",
  });
  await stagehand.init();

  const browser = await chromium.connectOverCDP({
    wsEndpoint: stagehand.connectURL(),
  });
  const context = browser.contexts()[0];

  const results = [];
  for (const url of urls) {
    const page = await context.newPage();
    await page.goto(url);

    const data = await stagehand.extract(
      "Extract the main article title, author, and publication date",
      z.object({
        title: z.string(),
        author: z.string().optional(),
        date: z.string().optional(),
      }),
      { page }
    );

    results.push({ url, ...data });
    await page.close();
  }

  await stagehand.close();
  return results;
}
```

### 模板 3: 条件分支自动化（observe 驱动）

```typescript
async function adaptiveWorkflow() {
  const stagehand = new Stagehand({ env: "LOCAL" });
  await stagehand.init();
  const page = stagehand.context.pages()[0];

  await page.goto("https://example.com/dashboard");

  // 观察当前页面状态
  const elements = await stagehand.observe("check if there is a cookie consent banner");

  if (elements.length > 0) {
    await stagehand.act("accept the cookie consent");
  }

  // 根据页面内容决定下一步
  const navItems = await stagehand.observe("find all main navigation items");
  const hasReports = navItems.some(item =>
    item.description?.toLowerCase().includes("report")
  );

  if (hasReports) {
    await stagehand.act("click on the Reports section");
  } else {
    await stagehand.act("click on the Dashboard section");
  }

  await stagehand.close();
}
```

---

## 常见踩坑

### 1. act() 指令过于复杂

```typescript
// 错误：一条指令做多件事
await stagehand.act("open filters, select 4-star, click apply");

// 正确：拆分为单步
await stagehand.act("open the filters panel");
await stagehand.act("choose 4-star rating");
await stagehand.act("click the apply button");
```

### 2. extract() Schema 过于严格

```typescript
// 错误：价格可能带货币符号，z.number() 会失败
z.object({ price: z.number() })

// 正确：用 string 接收，后续代码处理
z.object({ price: z.string().describe("price including currency symbol") })
```

### 3. 忽略页面加载状态

```typescript
// 错误：页面还没加载完就提取
await page.goto("https://example.com");
await stagehand.extract("...");

// 正确：等待内容就绪
await page.goto("https://example.com");
await page.waitForLoadState("domcontentloaded");
await stagehand.extract("...");
```

### 4. 生产环境未启用缓存

```typescript
// 开发可以不缓存，生产必须开启
const stagehand = new Stagehand({
  env: "BROWSERBASE",
  cacheDir: "cache/production-flow", // 生产必加
});
```

### 5. 无头环境缺少系统依赖

Linux 无头模式需安装：
```bash
apt-get install -y libnss3-dev libatk-bridge2.0-dev libgtk-3-dev libxss1 libasound2
```

---

## 安装与快速开始

```bash
# 方式 1: 脚手架（推荐新手）
npx create-browser-app

# 方式 2: 手动安装到现有项目
npm install @browserbasehq/stagehand zod dotenv

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 LLM API Key

# 运行
npx tsx your-script.ts
```

---

## 适用场景矩阵

| 场景 | 推荐工具 | 理由 |
|------|---------|------|
| CI/CD 回归测试（固定页面） | 纯 Playwright | 零 LLM 成本，确定性高 |
| E2E 测试（页面频繁改版） | Stagehand + Playwright 混合 | AI 自愈 + 代码断言 |
| 爬虫/数据采集 | Stagehand extract() | 免写解析逻辑 |
| RPA 内部工具自动化 | Stagehand act() + 代码 | 不确定的 UI 交给 AI |
| 多网站统一流程 | Stagehand agent() | 一个脚本适配多站 |
| 性能测试/压测 | 纯 Playwright | 无 LLM 开销 |

---

## 参考资料

- **GitHub**: https://github.com/browserbase/stagehand (21K+ Stars)
- **文档**: https://docs.stagehand.dev
- **Python SDK**: https://github.com/browserbase/stagehand-python
- **MCP 集成**: https://docs.stagehand.dev/integrations/mcp/introduction
- **Changelog**: https://github.com/browserbase/stagehand/releases

---

## Version History

- **v1.0.0** (2026-02-26) - 初始版本，完整覆盖 act/extract/observe/agent 四大核心能力
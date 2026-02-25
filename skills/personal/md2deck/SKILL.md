# md2deck — Markdown 投研报告 → 演示文稿生成 Skill

## Description

将投研报告 Markdown 转换为专业演示文稿。双渲染引擎：Marp（视觉优先，HTML/PDF 演示）+ python-pptx（可编辑 .pptx 交付）。共享统一设计规范。

适用关键词：生成 PPT、投研 PPT、路演幻灯片、Markdown 转 PPT、Pitch Deck。

---

## 架构

```
投研报告 Markdown（source of truth）
         │
    ┌────┴────┐
    ▼         ▼
  Marp       python-pptx
  (CSS)      (模板.pptx)
    │         │
    ▼         ▼
 HTML/PDF   可编辑 .pptx
 (演示用)    (交付用)
```

**两套引擎共享同一套设计规范**（品牌色、字体、版式、Slide 结构）。

---

## 设计规范（Design Tokens）

### 配色方案

| Token | 值 | 用途 |
|-------|---|------|
| `--color-primary` | `#1A73E8` | 标题、强调色、CTA 按钮 |
| `--color-primary-dark` | `#0D47A1` | 深色标题、封面背景 |
| `--color-accent` | `#FF6D00` | 高亮数据、关键指标 |
| `--color-bg` | `#FFFFFF` | 正文背景 |
| `--color-bg-alt` | `#F5F7FA` | 交替行、卡片背景 |
| `--color-text` | `#212121` | 正文文字 |
| `--color-text-secondary` | `#757575` | 辅助文字、注释 |
| `--color-success` | `#2E7D32` | 正向指标（增长率、优势） |
| `--color-danger` | `#C62828` | 风险、负向指标 |

### 字体

| 用途 | 中文 | 英文/数字 | 备选 |
|------|------|----------|------|
| 标题 | 思源黑体 Bold | Inter Bold | Noto Sans SC Bold |
| 正文 | 思源黑体 Regular | Inter Regular | Noto Sans SC |
| 数据 | — | JetBrains Mono | Roboto Mono |

### Slide 版式模板

| Slide 类型 | 布局 | 适用场景 |
|-----------|------|---------|
| **cover** | 全幅背景 + 居中标题 + 副标题 + 融资信息 | 封面 |
| **section** | 大号标题居中 + 模块编号 | 章节过渡页 |
| **title-bullets** | 左侧标题 + 右侧 3-5 个要点 | 核心亮点、策略 |
| **data-table** | 标题 + 表格（交替行着色） | 市场数据、财务预测 |
| **comparison** | 双栏/四象限对比 | 竞品分析 |
| **funnel** | 漏斗图（TAM→SAM→SOM 或 收入漏斗） | 市场规模、商业模式 |
| **chart** | 标题 + 图表占位（折线/柱状/饼图） | 财务曲线、数据可视化 |
| **quote** | 大号引文 + 来源 | 核心洞察、愿景 |
| **team** | 头像 + 姓名 + 一句话背景（网格布局） | 团队介绍 |
| **cta** | 融资信息 + 联系方式 + 一句话愿景 | 结束页 |

---

## Slide 映射规则（投研报告 → Slides）

从 10 模块投研报告自动映射为 13-15 张 Slides：

| Slide # | 来源模块 | Slide 类型 | 内容提取规则 |
|---------|---------|-----------|-------------|
| 1 | 模块 1 执行摘要 | **cover** | 项目名 + 一句话定位 + 融资轮次金额 |
| 2 | 模块 1 执行摘要 | **title-bullets** | 核心亮点（3-5 bullets） |
| 3 | 模块 3 痛点 #1 | **data-table** | 痛点 1 + 数据佐证 |
| 4 | 模块 3 痛点 #2-3 | **title-bullets** | 痛点 2-3 + 现有方案不足 |
| 5 | 模块 4 产品方案 | **title-bullets** | 核心功能矩阵（top 4-6）+ 产品截图占位 |
| 6 | 模块 2 市场分析 | **funnel** | TAM / SAM / SOM 漏斗 |
| 7 | 模块 5 商业模式 | **data-table** | 五级收入漏斗 + ARPU + 付费率 |
| 8 | 模块 5 单位经济 | **title-bullets** | CAC / LTV / LTV÷CAC / 毛利率 |
| 9 | 模块 6 竞品分析 | **comparison** | 竞品矩阵表（精简到 4 列） |
| 10 | 模块 7 增长策略 | **title-bullets** | 增长渠道 top 3 + 裂变飞轮 |
| 11 | 模块 8 财务预测 | **chart** | 3 年收入曲线 + 盈亏平衡标注 |
| 12 | 模块 9 团队 | **team** | 核心成员 + 背景 |
| 13 | 模块 9 融资计划 | **data-table** | 本轮金额 + 资金用途 + 下一轮触发条件 |
| 14 | 模块 1 愿景 | **cta** | 愿景 slogan + 联系方式 |

---

## 渲染引擎 A：Marp（视觉优先）

### 安装

```bash
npm install -g @marp-team/marp-cli
# 或
brew install marp-cli
```

### 使用

```bash
# 生成 HTML（演示用）
marp slides.md --theme ./themes/pitch-deck.css --html --output slides.html

# 生成 PDF
marp slides.md --theme ./themes/pitch-deck.css --pdf --output slides.pdf

# 生成 PPTX（注意：为图片嵌入，不可编辑）
marp slides.md --theme ./themes/pitch-deck.css --pptx --output slides.pptx
```

### Marp Markdown 格式要求

```markdown
---
marp: true
theme: pitch-deck
paginate: true
---

<!-- _class: cover -->
# 项目名称
## 一句话定位
**天使轮融资 300-500 万元**

---

<!-- _class: title-bullets -->
# 核心亮点

- **精准切口**：聚焦 xxx 场景
- **双端设计**：xxx + xxx
- **轻量部署**：基于 xxx
- **商业闭环**：xxx → xxx → xxx

---
```

### 主题文件

自定义 CSS 主题位于 `themes/pitch-deck.css`，实现上述设计规范的全部 Token。

---

## 渲染引擎 B：python-pptx（可编辑交付）

### 安装

```bash
pip install python-pptx Pillow
```

### 使用

```bash
python scripts/md2pptx.py \
  --input report.md \
  --template templates/pitch-deck-template.pptx \
  --output output.pptx
```

### 工作原理

1. 解析 Markdown 结构（按 `## 模块` 分章节，提取标题、表格、bullet list）
2. 按 Slide 映射规则确定每张 Slide 的类型
3. 从模板 .pptx 中克隆对应版式（Layout）
4. 填充文本、表格、占位图到 Placeholder
5. 应用设计规范（字体、颜色、间距）
6. 输出可编辑 .pptx

### 模板说明

`templates/pitch-deck-template.pptx` 需在 PowerPoint / Keynote 中预先设计，包含以下 Slide Layouts：

- Layout 0: cover
- Layout 1: section
- Layout 2: title-bullets
- Layout 3: data-table
- Layout 4: comparison
- Layout 5: funnel
- Layout 6: chart
- Layout 7: quote
- Layout 8: team
- Layout 9: cta

---

## 工作流程

### 完整流程

1. **投研报告 Skill** 生成 10 模块 Markdown（已有）
2. 用户说 *"生成 PPT"* / *"转成幻灯片"*
3. **md2deck Skill** 触发：
   a. 解析 Markdown，提取各模块内容
   b. 按映射规则生成 Slide 内容
   c. **同时输出两个版本**：
      - Marp Markdown → HTML/PDF（演示用）
      - python-pptx → .pptx（交付用）
4. 用户根据场景选择使用哪个版本

### AI 协作说明

当用户请求生成 PPT 时，AI 应：

1. 读取投研报告 Markdown
2. 按 Slide 映射规则提取每张 Slide 的内容
3. 生成 Marp 格式的 `slides.md`（可直接用 marp-cli 渲染）
4. 如需可编辑 .pptx，提示用户运行 `python scripts/md2pptx.py`
5. 两个版本的内容和结构保持一致，仅渲染方式不同

---

## Review 检查清单

- [ ] 每张 Slide 只传达 1 个核心信息
- [ ] 文字密度 ≤ 50 词/Slide（中文 ≤ 80 字）
- [ ] 关键数据用 `--color-accent` 高亮
- [ ] 表格行数 ≤ 6（超过的拆分到多张 Slide）
- [ ] 封面包含项目名 + 定位 + 融资信息
- [ ] 结尾包含愿景 + 联系方式 + CTA
- [ ] Marp 版本和 pptx 版本内容一致
- [ ] 所有数据来源与原报告一致

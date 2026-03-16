---
title: SKILL
type: note
permalink: engineering-playbook/skills/personal/md2deck/skill
---

# md2deck — Markdown 投研报告 → 演示文稿生成 Skill

## Description

将投研报告 Markdown 转换为专业演示文稿。双渲染引擎：Marp（视觉优先，HTML/PDF 演示）+ python-pptx（可编辑 .pptx 交付）。共享统一设计规范。

**v3.0 新特性**：
- `--compact` 紧凑模式（只保留核心 Slide，适合路演）
- `--charts` 图表模式（混合引擎：原生可编辑图表 + matplotlib 图片）
- 三套配色风格（Professional / Minimal / Modern）

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

## 风格主题（三套可选）

| 风格 | CSS 文件 | python-pptx `--style` | 视觉特征 |
|------|---------|----------------------|---------|
| **Professional**（默认） | `themes/pitch-deck.css` | `professional` | 深蓝商务底色 + 渐变强调色 + 精致表格阴影 |
| **Minimal** | `themes/minimal.css` | `minimal` | 大量留白 + 纯黑白灰 + 橙色点缀 + 极简线条 |
| **Modern** | `themes/modern.css` | `modern` | 深色背景 + 紫蓝渐变 + 科技感光晕效果 |

三套风格共享同一套 Slide 类型（cover / section / title-bullets / data-table / comparison / quote / cta），仅配色和视觉风格不同。

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
# Professional 风格
marp slides.md --theme ./themes/pitch-deck.css --html --output slides.html

# Minimal 风格
marp slides.md --theme ./themes/minimal.css --html --output slides.html

# Modern 风格
marp slides.md --theme ./themes/modern.css --html --output slides.html

# 导出 PDF
marp slides.md --theme ./themes/pitch-deck.css --pdf --output slides.pdf

# 导出 PPTX（注意：图片嵌入，不可编辑）
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
pip install matplotlib  # 可选，仅 --charts 需要
```

### 使用

```bash
# 完整模式（默认，所有模块+子章节）
python scripts/md2pptx.py -i report.md -o output.pptx -s professional

# 紧凑模式（只保留核心 Slide，适合路演）
python scripts/md2pptx.py -i report.md -o output.pptx -s professional --compact

# 启用图表（自动生成柱状图/折线图/饼图/漏斗图）
python scripts/md2pptx.py -i report.md -o output.pptx -s professional --charts

# 紧凑 + 图表（推荐路演场景）
python scripts/md2pptx.py -i report.md -o output.pptx --compact --charts
```

### 风格选项

```bash
# Professional（默认）— 深蓝商务
python scripts/md2pptx.py -i report.md -o output.pptx -s professional

# Minimal — 极简黑白灰
python scripts/md2pptx.py -i report.md -o output.pptx -s minimal

# Modern — 科技感深色
python scripts/md2pptx.py -i report.md -o output.pptx -s modern
```

### 模式对比

| 模式 | 产出 Slide 数 | 图表 | 适合场景 |
|------|-------------|------|---------|
| 默认 | 45-50 张 | 无 | 完整数据呈现、尽职调查 |
| `--compact` | 20-25 张 | 无 | 路演 Pitch、快速浏览 |
| `--charts` | +7 张图表 | 5 原生 + 2 图片 | 数据可视化增强 |
| `--compact --charts` | 30-35 张 | 同上 | 路演 + 可视化（推荐） |

### 图表引擎（混合方案）

采用 **python-pptx 原生 Chart + matplotlib 图片**混合策略：

| 图表类型 | 引擎 | 可编辑 | 说明 |
|---------|------|--------|------|
| 柱状图（收入/成本/场景对比） | python-pptx 原生 | ✅ 投资人可直接修改数据 | `add_chart(COLUMN_CLUSTERED)` |
| 折线图（运营指标趋势） | python-pptx 原生 | ✅ | `add_chart(LINE)` |
| 饼图（资金用途占比） | python-pptx 原生 | ✅ | `add_chart(PIE)` |
| 漏斗图（TAM/SAM/SOM） | matplotlib 图片 | ❌ | python-pptx 不支持漏斗型 |
| 四象限图（竞品定位） | matplotlib 图片 | ❌ | 自定义散点图+象限线 |

**为什么不用 Plotly**：导出静态图需 kaleido（Chromium 内核，200MB+），ARM Mac 兼容问题多，CI 环境配置复杂。PPT 中是静态图，Plotly 的交互优势用不上。

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

---

## PPT 质量评估标准（6 维度评分体系）

用于评估生成 PPT 的质量，每个维度 1-5 分，总分 30 分。

### 维度 1：数据完整性（Data Completeness）

| 分数 | 标准 |
|------|------|
| 5 | 原报告所有关键数据（表格、指标、来源）100% 完整呈现 |
| 4 | 关键数据 ≥ 90%，仅缺少辅助性数据 |
| 3 | 关键数据 70-90%，有重要数据遗漏但不影响整体理解 |
| 2 | 关键数据 < 70%，多处核心数据缺失 |
| 1 | 严重缺失，无法从 PPT 获取完整信息 |

**检查要点**：
- 财务预测三年数据是否完整
- TAM/SAM/SOM 数值是否准确
- 竞品对比维度是否齐全
- 数据来源是否标注

### 维度 2：数据准确性（Data Accuracy）

| 分数 | 标准 |
|------|------|
| 5 | 所有数据与原报告完全一致，无错误 |
| 4 | 99% 准确，仅有极个别四舍五入差异 |
| 3 | 有 1-2 处数据错误，但非核心指标 |
| 2 | 有核心数据错误（如收入、估值等） |
| 1 | 多处核心数据错误，严重误导 |

### 维度 3：视觉设计（Visual Design）

| 分数 | 标准 |
|------|------|
| 5 | 专业设计师水平：配色和谐、层次清晰、留白合理、品牌感强 |
| 4 | 优秀：风格统一、视觉舒适、主次分明 |
| 3 | 合格：基本美观，无明显设计问题 |
| 2 | 较差：排版混乱、配色不协调、元素拥挤 |
| 1 | 极差：像纯文本堆砌，无设计感 |

**检查要点**：
- 配色是否统一且专业
- 字体大小层次是否清晰（标题 > 副标题 > 正文 > 注释）
- 留白是否充足（内容不贴边）
- 对齐是否整齐（文本、表格、图表）
- 装饰元素（分割线、圆点、渐变）是否恰到好处

### 维度 4：信息架构（Information Architecture）

| 分数 | 标准 |
|------|------|
| 5 | 叙事逻辑清晰：痛点→方案→市场→模式→数据→团队→融资，有节奏感 |
| 4 | 逻辑通顺，章节衔接自然 |
| 3 | 结构合理但缺乏过渡，略显生硬 |
| 2 | 结构混乱，关键信息位置不当 |
| 1 | 无逻辑，信息堆砌 |

**检查要点**：
- 是否遵循投资人阅读习惯（先抓痛点 → 再给方案 → 用数据证明）
- 章节过渡页是否自然
- 每张 Slide 是否只聚焦一个主题
- compact 模式是否保留了完整的叙事线

### 维度 5：可编辑性与交互（Editability & Interaction）

| 分数 | 标准 |
|------|------|
| 5 | 原生可编辑：所有文本/表格/图表可直接修改，无图片化内容 |
| 4 | 大部分可编辑，仅个别图表为图片 |
| 3 | 文本和表格可编辑，图表为图片 |
| 2 | 部分内容图片化，修改困难 |
| 1 | 整体为图片嵌入，完全不可编辑 |

### 维度 6：文件质量（File Quality）

| 分数 | 标准 |
|------|------|
| 5 | 文件体积合理（< 5MB），打开流畅，兼容 PowerPoint / Keynote / Google Slides |
| 4 | 体积适中（5-15MB），主流软件可打开 |
| 3 | 体积偏大（15-30MB），打开略慢 |
| 2 | 体积过大（> 30MB），或兼容性问题 |
| 1 | 文件损坏或无法打开 |

### 评分参考

| 总分 | 等级 | 说明 |
|------|------|------|
| 27-30 | ⭐⭐⭐⭐⭐ | 专业级，可直接用于投资人路演 |
| 22-26 | ⭐⭐⭐⭐ | 优秀，微调后可用 |
| 17-21 | ⭐⭐⭐ | 合格，需要人工优化 |
| 12-16 | ⭐⭐ | 较差，需大幅修改 |
| 6-11 | ⭐ | 不合格，需重新生成 |

---

## 开源 PPT 模板资源参考

以下为调研后的开源/免费模板资源，可作为 `--template` 参数的母版基础：

| 平台 | 类型 | 免费 | 质量 | 适合场景 | 链接 |
|------|------|------|------|---------|------|
| **Slidesgo** | Pitch Deck 模板 | ✅ 免费版（3个/月） | ⭐⭐⭐⭐⭐ | 投资路演、商业计划 | [slidesgo.com/pitch-deck](https://slidesgo.com/pitch-deck) |
| **Pitch.com** | Pitch Deck 模板 | ✅ 完全免费 | ⭐⭐⭐⭐⭐ | 初创公司路演 | [pitch.com/templates](https://pitch.com/templates) |
| **Canva** | 通用 PPT 模板 | ✅ 免费版 | ⭐⭐⭐⭐ | 多场景通用 | [canva.com/presentations](https://www.canva.com/presentations/templates/) |
| **WPS 模板** | 中文商务模板 | ✅ 部分免费 | ⭐⭐⭐ | 中文商务场景 | [template.wps.com](http://template.wps.com/) |
| **Google Slides** | 内置模板 | ✅ | ⭐⭐⭐ | 快速轻量 | Google Slides 内置 |

**使用建议**：
1. 从 Slidesgo / Pitch.com 下载高质量 `.pptx` 母版模板
2. 在 PowerPoint/Keynote 中调整 Slide Layouts 布局
3. 通过 `--template` 参数加载：`python scripts/md2pptx.py -i report.md -o out.pptx --template my-template.pptx`
4. 脚本会基于母版的 Layout 0-9 填充内容，视觉效果远超纯代码生成
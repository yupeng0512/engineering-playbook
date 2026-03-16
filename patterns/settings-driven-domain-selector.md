---
title: settings-driven-domain-selector
type: note
permalink: engineering-playbook/patterns/settings-driven-domain-selector
---

# 设置驱动的选择器模式：消除重复手动输入

## 场景

用户需要在多个页面反复输入相同的配置值（如域名、API 端点、邮箱地址），每次都要去其他地方复制粘贴。

## 问题

TradeRadar 送达率页面中，用户每次检查域名或启动预热都要手动输入域名字符串。这不仅体验差（需要切换到域名服务商网站复制粘贴），而且容易输入错误，同一域名无法在多个功能间复用。

## 方案

**Settings-Driven Selector** 模式：

1. **在 Settings 统一管理**：提供增删改查界面，数据持久化到用户配置（如 JSONB 字段）
2. **在使用处提供 Selector**：通过下拉组件从已配置数据中选择，支持多选
3. **保留手动输入后门**：Selector 底部保留手动输入入口，用于临时添加未配置的值
4. **批量操作**：多选后提供批量操作按钮，减少重复点击

## 关键设计决策

| 决策点 | 选择 | 理由 |
|--------|------|------|
| 数据存储 | JSONB 数组 in user settings | 免新建表，后端 API 不用改 |
| Selector 位置 | 替代原 Input | 减少认知负担，老用户无适应成本 |
| 手动输入 | Selector 下拉面板底部 | 兼顾灵活性，不阻塞未配置场景 |
| 批量请求 | Promise.allSettled 并行 | 串行 for-await 在 5+ 域名时延迟明显 |

## Code Review Checklist

此模式实现时常见的遗漏：
- [ ] Selector 组件内的文案是否全部走 i18n（容易硬编码 "Select all"）
- [ ] 校验逻辑是否 DRY（Input onKeyDown vs Button onClick 容易复制粘贴）
- [ ] 批量请求用 Promise.allSettled 而非串行 for-await
- [ ] Checkbox 部分选中时是否有 indeterminate 视觉状态
- [ ] 按钮是否有 shrink-0 / whitespace-nowrap 防止文字换行

## Observations

- [pattern] 用户需要反复输入的值应提前配置到 Settings，使用时通过选择器引用 #ux #settings-driven
- [technique] JSONB 字段存储数组配置是零迁移成本的方案 #jsonb #postgres
- [insight] Code review 应重点检查 i18n 硬编码和批量请求的并发模式 #code-review

## Relations

- relates_to [[frontend-backend-data-sync]]
- part_of [[TradeRadar]]

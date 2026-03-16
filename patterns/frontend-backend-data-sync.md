---
title: frontend-backend-data-sync
type: note
permalink: engineering-playbook/patterns/frontend-backend-data-sync
---

# 前后端数据一致性：Single Source of Truth

## 场景

SaaS 产品中，涉及套餐/定价/功能限额等业务数据，前端和后端各自硬编码导致数据不一致。

## 问题

TradeRadar Phase 6 中，billing 页面前端硬编码了套餐限额（如 Starter 2000 邮件），而后端 `PlanDefaults` 实际限额为 1000。用户看到的功能承诺与实际执行不符，构成功能性欺骗风险。

## 根因

- 前端开发时参考了旧的或未确认的数据
- 后端调整限额后没有同步更新前端
- 没有从设计上防止这种漂移

## 解法

**后端作为唯一数据源，前端动态获取**

```go
// 后端定义 PlanCatalog 包含价格和限额
var PlanCatalog = map[string]PlanSpec{
    "free":    {Price: 0, Limits: PlanDefaults["free"]},
    "starter": {Price: 29, Limits: PlanDefaults["starter"]},
    "pro":     {Price: 79, Limits: PlanDefaults["pro"]},
}

// API 返回完整目录
c.JSON(http.StatusOK, gin.H{
    "plan":  currentPlan,
    "plans": service.PlanCatalog,
})
```

```typescript
// 前端从 API 获取，不硬编码
const [planCatalog, setPlanCatalog] = useState<Record<string, PlanSpec>>({});

const res = await fetch("/api/v1/billing/status", { headers });
if (data.plans) setPlanCatalog(data.plans);
```

## 推广原则

| 场景 | 做法 |
|------|------|
| 定价/套餐 | 后端 `PlanCatalog` 为唯一源 |
| 功能开关 | 后端 feature flags API |
| 表单选项（国家/行业） | 后端枚举 API 或 i18n 文件 |
| 临时文案（营销文字） | CMS 或配置中心 |

## Checklist

- [ ] 前端是否有任何业务关键数字（价格、限额、百分比）是硬编码的？
- [ ] 如果后端改了某个配置值，前端是否需要同步修改？如果需要，就是 bug 来源
- [ ] API 是否返回了前端渲染所需的全部数据？

## 来源

TradeRadar Phase 6.5 Review — 发现前端 billing 页面硬编码套餐数据与后端 PlanDefaults 严重偏差（2-5倍）。
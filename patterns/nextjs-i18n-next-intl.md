---
title: Next.js App Router i18n with next-intl
category: frontend
tags:
- i18n
- next-intl
- next.js
- app-router
- internationalization
created: 2026-03-10
project: trade-radar
permalink: engineering-playbook/patterns/nextjs-i18n-next-intl
---

# Next.js App Router i18n with next-intl

## 场景

Next.js 15 App Router 项目需要支持多语言（中/英），要求：
- URL 带 locale 前缀（`/en/dashboard`, `/zh/dashboard`）
- SSG 兼容（`generateStaticParams`）
- 组件内翻译无需 prop drilling

## 方案选型

| 方案 | 优势 | 劣势 |
|------|------|------|
| **next-intl** ✅ | App Router 原生支持，类型安全，SSG 友好 | 需要 `[locale]` 路由层 |
| next-i18next | Pages Router 时代标准 | App Router 支持不完善 |
| react-intl | 生态大 | 需手动集成 routing |
| 自建方案 | 灵活 | 维护成本高 |

## 目录结构

```
web/
├── messages/
│   ├── en.json          # 英文翻译
│   └── zh.json          # 中文翻译
├── src/
│   ├── i18n/
│   │   ├── request.ts   # getRequestConfig
│   │   └── routing.ts   # defineRouting (locales, defaultLocale)
│   ├── middleware.ts     # createMiddleware(routing)
│   └── app/
│       └── [locale]/
│           ├── layout.tsx          # NextIntlClientProvider
│           ├── (dashboard)/
│           │   ├── customers/
│           │   ├── products/
│           │   └── ...
│           └── (auth)/
│               └── login/
└── next.config.ts       # createNextIntlPlugin()
```

## 关键配置

### `i18n/routing.ts`

```typescript
import { defineRouting } from 'next-intl/routing';
export const routing = defineRouting({
  locales: ['en', 'zh'],
  defaultLocale: 'en'
});
```

### `middleware.ts`

```typescript
import createMiddleware from 'next-intl/middleware';
import { routing } from './i18n/routing';
export default createMiddleware(routing);
export const config = { matcher: ['/', '/(en|zh)/:path*'] };
```

### `[locale]/layout.tsx`

```typescript
import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';

export function generateStaticParams() {
  return routing.locales.map(locale => ({ locale }));
}

export default async function Layout({ children, params }) {
  const { locale } = await params;
  const messages = await getMessages();
  return (
    <NextIntlClientProvider messages={messages}>
      {children}
    </NextIntlClientProvider>
  );
}
```

### 组件中使用

```typescript
import { useTranslations } from 'next-intl';

function CustomerPage() {
  const t = useTranslations('customers');
  return <h1>{t('title')}</h1>;
}
```

## 踩坑记录

1. **next.config.ts 必须用 `createNextIntlPlugin` 包裹**，否则 Server Components 中 `getMessages()` 报错
2. **翻译 JSON 嵌套结构**要和 `useTranslations` 的 namespace 一致：`useTranslations('nav')` 对应 `{ "nav": { ... } }`
3. **动态路由页面**需要 `generateStaticParams` 返回所有 locale，否则 SSG 构建失败
4. **middleware matcher** 必须包含 `/` 根路径，否则首次访问不会自动 redirect 到默认 locale
5. **Link 组件**：使用 `next-intl` 提供的 `Link` 组件自动带 locale 前缀
6. **新增功能页面的 i18n 清单**（Phase 6 经验）：
   - `nav` 中新增导航键 → `sidebar.tsx` 使用 `t("nav.xxx")`
   - 新建独立 namespace（如 `billing`、`deliverability`）→ 新页面 `useTranslations("billing")`
   - 嵌套键用 `.` 分隔（如 `t("warmup.title")`、`t("features.customers")`）
   - **en.json 和 zh.json 必须同步维护**，键缺失会导致 fallback 显示键名而非文本
   - **类型安全技巧**：`t(key as "free" | "starter" | "pro")` 用 union type 约束动态键

## 关联

- `part_of` [[trade-radar]] — TradeRadar 项目国际化实现
- `relates_to` [[nextjs-app-router]] — Next.js App Router 最佳实践
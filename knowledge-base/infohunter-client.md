# InfoHunter Client 完整经验档案

> 项目周期: 2025 ~ 进行中
> 最后更新: 2026-02-25
> 状态: 活跃开发

---

## 项目概要

| 维度 | 说明 |
|------|------|
| **类型** | 双端客户端（iOS/Android App + Web 管理端） |
| **领域** | AI 社交媒体监控 |
| **规模** | pnpm Monorepo，三包结构（mobile + web + shared） |
| **核心价值** | InfoHunter 后端的用户端，信息流消费 + 订阅管理 |

### 核心技术栈

| 层级 | 技术 | 版本 | 备注 |
|------|------|------|------|
| App 框架 | React Native | 0.81.5 | New Architecture 启用 |
| App SDK | Expo | SDK 54 (~54.0.33) | |
| App 路由 | expo-router | ~6.0.23 | 文件路由 |
| Web 构建 | Vite | ^7.3.1 | |
| Web CSS | Tailwind CSS | ^4.1.0 | v4 原子化 |
| UI 核心 | React | 19.1.4 | CVE-2025-55182 安全版本 |
| 数据管理 | TanStack Query | ^5.60.0 | |
| 客户端状态 | Zustand | ^5.0.0 | |
| HTTP | Axios | ^1.7.0 | Token 刷新拦截器 |
| 语言 | TypeScript | ~5.9.x | |
| 包管理 | pnpm | 10.30.1 | Workspace Monorepo |
| 高性能列表 | @shopify/flash-list | 2.0.2 | |

### 架构概览

```
pnpm Monorepo
├── apps/mobile/     Expo Router → React Native App
│     ├── (tabs)/      底部 Tab: 今日/发现/我的
│     ├── auth/        登录/注册
│     ├── content/     内容详情
│     └── subscription/ 订阅管理
├── apps/web/        Vite → React SPA 管理端
│     ├── Dashboard    概览
│     ├── Feed         内容流
│     ├── Subscriptions 订阅管理
│     ├── Costs        成本统计
│     └── Settings     设置
└── packages/shared/ 两端共享层
      ├── types/       7 个类型定义文件
      ├── api/         Axios client + 40+ 端点
      ├── hooks/       7 个 TanStack Query hooks
      └── utils/       格式化工具
```

---

## 做得好的地方

### 技术选型

#### pnpm Monorepo 三包结构

- **技术**: pnpm 10 + workspace:* + shared package
- **场景**: 双端（App + Web）代码复用
- **选择理由**: 严格依赖管理 + workspace 协议 + patch 能力
- **实际效果**: Types/API/Hooks/Utils 100% 复用，UI 组件各端独立
- **推荐指数**: 5/5
- **适用建议**: 有多端需求的 TypeScript 项目标配

#### TanStack Query Hook 工厂模式

- **技术**: Query Key 工厂 + 层级式 key 结构
- **实际效果**: `contentKeys.list(filters)` → 精准 invalidation，mutation 后自动刷新
- **推荐指数**: 5/5

### 架构设计

#### 共享层四层复用

- **解决的问题**: App 端和 Web 端大量重复代码
- **实现方式**: `packages/shared` 导出 types + api + hooks + utils
- **复用率**: Types 100% / API 100% / Hooks 100% / Utils 100% / UI 0%（各端独立）
- **可复用程度**: 高
- **复用注意事项**: Web 端通过 Vite `resolve.alias` 直接引用源码，零构建开发

#### Token 刷新拦截器（并发安全）

- **解决的问题**: JWT token 过期时的透明刷新
- **实现方式**: Axios 拦截器 401 → 共享 `_refreshPromise` 防重复刷新 → 成功后重放请求 → 失败触发登出
- **可复用程度**: 高
- **复用注意事项**: 模块级变量管理 token（非 React state），避免 re-render

#### 双机协作开发流程

- **解决的问题**: Linux Cloud 无法运行 iOS Simulator
- **实现方式**: Cloud (Cursor) 编码 → git push → Mac pull + build + Simulator
- **关键**: 4 个 bash 脚本自动化（run-ios / rebuild-ios / dev / fix-canary-versions）
- **可复用程度**: 中
- **复用注意事项**: 适用于远程开发 + 本地 native 构建的场景

---

## 做得不好的地方

### 踩坑清单

#### 坑 1: CVE-2025-55182 安全修复链（最大坑）

- **影响程度**: 高（CVSS 10.0 RCE）
- **耗时**: 约 1 天
- **现象**: React 19.1.0 存在 Server Components RCE 漏洞，升级到 19.1.4 后 RN 崩溃
- **根因**: RN 0.81.5 renderer 硬编码检查 `react@19.1.0`
- **解决方案**: 四层修复
  1. `pnpm.overrides` 锁定 react 19.1.4
  2. `pnpm patch react-native@0.81.5` 修补 6 个 renderer 版本号
  3. `postinstall` 脚本修补 `@expo/cli` 内嵌 canary react
  4. **禁止** `experiments.reactCanary: true`（会加载 canary renderer 导致版本不匹配）
- **预防建议**: 安全升级 React 版本时，必须检查 RN renderer 的版本绑定

#### 坑 2: Metro 不识别 pnpm workspace 包

- **影响程度**: 高
- **现象**: Metro bundler 找不到 `@infohunter/shared` 模块
- **根因**: Metro 默认不识别 pnpm 的 symlink workspace 结构
- **解决方案**: `metro.config.js` 三项配置
  - `watchFolders = [monorepoRoot]`
  - `resolver.nodeModulesPaths` 包含项目级和根级
  - `resolver.disableHierarchicalLookup = true`
- **预防建议**: RN + pnpm Monorepo 必须从第一天就配好 Metro

#### 坑 3: reactCanary flag 冲突

- **影响程度**: 高
- **现象**: 设置 `experiments.reactCanary: true` 后应用崩溃
- **根因**: 该 flag 让 Expo 加载 canary renderer，与 pnpm patch 修补过的版本冲突
- **解决方案**: 删除该 flag，在 CLAUDE.md 和 security.mdc 中标记为禁止操作
- **预防建议**: Expo 实验性 flag 需要逐个验证，不能盲目启用

#### 坑 4: iOS HTTP 请求被拦截

- **影响程度**: 中
- **现象**: App 无法连接后端 API
- **根因**: iOS 默认禁止 HTTP（仅允许 HTTPS），开发环境后端是 HTTP
- **解决方案**: `app.json` 中 `NSAllowsArbitraryLoads: true`
- **预防建议**: RN/Expo 连非 HTTPS 后端时，第一时间配好 ATS

#### 坑 5: expo-notifications API 破坏性变更

- **影响程度**: 低
- **现象**: `removeNotificationSubscription` 方法不存在
- **根因**: expo-notifications 0.32+ 移除了该方法
- **解决方案**: 改用 `subscription.remove()` 返回值模式
- **预防建议**: Expo SDK 升级后检查 Breaking Changes 文档

#### 坑 6: Duplicate React 问题

- **影响程度**: 高
- **现象**: "Invalid hook call" 错误
- **根因**: pnpm 严格依赖隔离导致多个 React 实例
- **解决方案**: `.npmrc` 设置 `node-linker=hoisted`
- **预防建议**: RN 项目使用 pnpm 必须设置 hoisted 模式

---

## 可复用资产

### 代码模式

- **pnpm Monorepo 三包结构**: 双端 + shared 的标准组织方式
- **Token 刷新拦截器**: Axios 401 自动刷新 + 并发去重 + 失败登出
- **Query Key 工厂**: 层级式 TanStack Query key 设计
- **CVE 修复四层方案**: pnpm overrides + patch + postinstall + flag 禁用
- **Expo Push 全链路**: 权限 → Token → 注册 → 设备检测 → 模拟器兼容

### 配置模板

- **metro.config.js**: pnpm Monorepo 下的 Metro 配置
- **iOS 构建脚本**: 4 个 bash 脚本自动化远程开发 + 本地构建

---

## 给未来自己的建议

### 如果重新做这个项目

1. 从第一天就配好 Metro + pnpm 的兼容配置，不要等报错再修
2. React 版本锁定策略在项目初始化时就确定，不要等安全漏洞逼迫升级
3. 共享层建为独立 npm 包（含 build），而非直接引用源码，避免各端构建工具差异

### 延伸到其他项目的通用建议

- **RN + pnpm Monorepo**: 必须 `node-linker=hoisted` + Metro watchFolders + disableHierarchicalLookup
- **React 安全升级**: 升级前检查 RN renderer 版本绑定，准备好 pnpm patch
- **双端复用**: Types + API + Hooks 共享，UI 各端独立，是投入产出比最高的策略
- **双机协作**: 远程编码 + 本地 native 构建，用 git 同步 + 自动化脚本桥接

---

## 元数据

- **沉淀时间**: 2026-02-25
- **信息来源**: 代码分析 / Git log / .cursor/rules/ / 深度代码扫描
- **覆盖度评估**: 约 90%。遗漏：(1) Web 管理端的具体页面实现 (2) EAS Build 云端构建的实际使用经验 (3) Zustand 状态管理的具体使用细节

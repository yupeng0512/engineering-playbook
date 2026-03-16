---
title: React effect 只执行一次（回调引用会变时）
category: frontend
tags:
  - react
  - useEffect
  - ref
  - layout
  - next.js
created: 2026-03-12
project: trade-radar
permalink: engineering-playbook/patterns/react-effect-run-once-with-callback
---

# React effect 只执行一次（回调引用会变时）

## 场景

在 Layout 或根组件里有一个“自动触发一次”的逻辑（例如新手引导自动开始），effect 里需要调用来自 Context 的回调（如 `startTour()`）。若把该回调放进 effect 的依赖数组 `[startTour]`，则：

- 路由切换、父组件重渲染时，Context 提供的函数引用可能变化（例如其内部依赖了 `useRouter`、`useTranslations` 等）。
- effect 会因依赖变化而重新执行：先 cleanup，再重新跑一遍，往往再次注册一个“延迟执行”（如 setTimeout），导致**同一逻辑被触发第二次**，表现为状态被重置、引导从第一步重新开始等“反复横跳”。

## 正确写法

**目标**：只在组件**真正挂载时**执行一次自动逻辑，不因回调引用变化而重跑。

用 **ref 保存最新回调**，effect **依赖为空数组**，内部调用 `ref.current()`：

```tsx
function TourAutoStarter() {
  const { startTour } = useProductTour();
  const startTourRef = useRef(startTour);
  startTourRef.current = startTour;

  useEffect(() => {
    const completed = localStorage.getItem("tour_completed");
    if (completed) return;
    const timer = window.setTimeout(() => {
      startTourRef.current();
    }, 900);
    return () => window.clearTimeout(timer);
  }, []); // 仅挂载时执行一次

  return null;
}
```

- 每次渲染都更新 `startTourRef.current`，保证调用到的是最新实现。
- effect 只跑一次，不会因 `startTour` 引用变化而再次触发“自动开始”。

## 反例（会反复触发）

```tsx
useEffect(() => {
  const timer = window.setTimeout(() => void startTour(), 900);
  return () => window.clearTimeout(timer);
}, [startTour]); // 路由/重渲染导致 startTour 变 → effect 重跑 → 900ms 后又 startTour()
```

## 适用场景

- Layout 内“只做一次”的自动行为：引导、埋点、弹窗一次提示等。
- 回调来自 Context / 上层 props，且其引用会随路由或其它 state 变化时。

## 参考

- TradeRadar 产品引导“反复横跳”修复：`web/src/app/[locale]/(dashboard)/layout.tsx` 中 `TourAutoStarter`（2026-03-12）。

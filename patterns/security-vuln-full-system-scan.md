# Pattern: 安全漏洞修复 — 全系统扫描思维

> 来源项目: infohunter-client / ops-dashboard | 推荐指数: 5/5 | 适用范围: 开发机上处理高危组件漏洞工单

## 适用场景

- 收到安全扫描平台（如 tsec）的高危组件漏洞工单
- 修复后工单反复出现、无法关闭
- 需要彻底清除某个依赖的所有残留版本

## 问题根因

开发者修复漏洞时，通常只关注项目 `node_modules/` 下的依赖版本，但安全扫描器扫描的是**整台宿主机的文件系统**。大量隐藏位置会残留漏洞版本：

| 隐藏位置 | 产生方式 | 典型路径 |
|----------|----------|----------|
| **npm npx 缓存** | `npx some-cli` 自动安装 | `~/.npm/_npx/*/node_modules/` |
| **pnpm content-addressable store** | pnpm 全局缓存 | `~/.local/share/pnpm/store/` |
| **Cursor/IDE worktree** | IDE 内部缓存 | `~/.cursor/worktrees/*/` |
| **Docker overlay** | 容器文件系统叠加层 | `/var/lib/docker/overlay2/*/` |
| **TypeScript 缓存** | `tsserver` 自动下载的类型定义 | `~/.cache/typescript/*/node_modules/` |
| **旧 node_modules 备份** | 手动 copy 或 mv | 任何位置 |

### 实际案例：CVE-2025-55182

React Server Components 远程代码执行漏洞。修复过程经历了 3 轮：

| 轮次 | 修复范围 | 结果 | 遗漏了什么 |
|------|----------|------|-----------|
| 第 1 轮 | `infohunter-client/node_modules/react` 从 19.1.0 → 19.1.4 | 工单复现 | pnpm store 残留 19.1.0 |
| 第 2 轮 | 清理 pnpm store + 提交修复 | 工单复现 | `~/.npm/_npx/` 下 `react@19.2.0-canary` |
| 第 3 轮 | 全系统 `find /` 扫描 + 删除所有残留 | 工单关闭 | — |

**三轮才修干净，根因就是每次只查了自己熟悉的位置。**

## 核心实现

### 修复漏洞后的验证脚本

修复完项目依赖后，必须用全系统扫描验证：

```bash
#!/bin/bash
# full-system-vuln-check.sh — 全系统检查某个 npm 包的漏洞版本
# 用法: ./full-system-vuln-check.sh react "19.0.0|19.1.0|19.1.1|19.2.0"

PKG_NAME="${1:?用法: $0 <包名> <漏洞版本正则>}"
VULN_PATTERN="${2:?用法: $0 <包名> <漏洞版本正则>}"

echo "=== 全系统扫描 $PKG_NAME 漏洞版本 ==="
echo "漏洞版本模式: $VULN_PATTERN"
echo ""

FOUND=0
while IFS= read -r f; do
    VER=$(python3 -c "
import json, sys
try:
    d = json.load(open('$f'))
    if d.get('name') == '$PKG_NAME':
        print(d.get('version', ''))
except: pass
" 2>/dev/null)

    if [ -n "$VER" ] && echo "$VER" | grep -qE "$VULN_PATTERN"; then
        echo "VULNERABLE  $PKG_NAME@$VER  $f"
        FOUND=$((FOUND + 1))
    fi
done < <(find / -name "package.json" -path "*/$PKG_NAME/package.json" \
    ! -path "/proc/*" ! -path "/sys/*" 2>/dev/null)

echo ""
if [ $FOUND -eq 0 ]; then
    echo "✅ ALL CLEAR — 未发现漏洞版本"
else
    echo "❌ 发现 $FOUND 处漏洞版本残留，请逐一清理"
fi
```

### 清理清单（修复后必做）

```
1. 项目 node_modules     → npm/pnpm install（升级版本）
2. pnpm store            → pnpm store prune
3. npm npx 缓存          → rm -rf ~/.npm/_npx/*
4. npm 全局缓存          → npm cache clean --force
5. IDE worktree 缓存     → 检查 ~/.cursor/worktrees/
6. Docker 容器           → 重建镜像 docker compose build --no-cache
7. 全系统验证            → 跑上面的脚本
```

## 决策矩阵：修复方式选择

| 依赖来源 | 修复方式 | 说明 |
|----------|----------|------|
| 项目直接依赖 | 升级 `package.json` + 重新安装 | 标准流程 |
| 间接/嵌套依赖 | `pnpm.overrides` / `npm.overrides` / `resolutions` | 强制覆盖子依赖版本 |
| CLI 工具内嵌 | 升级 CLI 工具本身 | 如 `@expo/cli` 内嵌的 react canary |
| npx 缓存 | 直接 `rm -rf ~/.npm/_npx/对应目录/` | npx 下次会自动重建 |
| Docker 镜像内 | 重建镜像或使用安全的基础镜像 | 纯静态前端镜像无 node_modules，不受影响 |
| 第三方镜像（如 joplin/server） | 自定义 Dockerfile 升级依赖 | 无法等官方更新时的应急方案 |

## 使用注意事项

1. **扫描器视角 ≠ 开发者视角**：扫描器检测 `package.json` 中的版本字符串，不管该包是否真正被加载执行
2. **18.x 不受 CVE-2025-55182 影响**：只有 19.0.0、19.1.0-19.1.1、19.2.0 在漏洞范围内
3. **canary 版本也会被检测**：`19.2.0-canary-xxxx` 同样匹配 19.2.0 的漏洞规则
4. **npx 缓存会"自愈"**：删除后下次 `npx` 会重新下载，如果上游已修复就不会再有问题
5. **pnpm overrides 只影响项目内**：对 `~/.npm/_npx/` 等全局位置无效，必须单独处理

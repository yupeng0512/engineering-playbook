---
title: review-before-write-generic-agent-context-capture
type: note
permalink: engineering-playbook/patterns/review-before-write-generic-agent-context-capture
---

# Review-Before-Write Generic Agent Context Capture

## 场景

很多带 Agent 的工作台产品都会遇到同一个诱惑：

- 用户在聊天里补了上下文
- Agent 看起来“已经理解了”
- 系统就想直接把这些内容写进数据库

这在 demo 阶段很顺，但一旦进入真实业务数据，很快会出问题。

## 问题

generic Agent 对话天然是高熵输入：

- 用户可能是在新增
- 也可能是在更新旧值
- 也可能只是临时讨论、并不想写库

如果系统直接写入，会出现三种常见故障：

- 用户以为只是讨论，系统却偷偷改了真数据
- 用户本来是在更新旧值，系统却当成新增 append
- 后续 Agent 自己都不知道数据库里的值和会话里的值哪个才是真相

## 推荐做法

### 1. generic Agent 先产出结构化变更提议

不要直接写库，先生成 proposal：

- `target_type`
- `target_id`
- `proposed_changes[]`
- `change_mode`
- `source`

每个字段至少要有：

- `before`
- `after`
- `mode`
- `reason`

### 2. 先判断“新增还是更新”

Agent 在提问或提议前，先读现有数据库值。

- 旧值为空：按“新增”处理
- 旧值不为空：按“更新”处理

这样用户能明确回答：

- 新补一项
- 更新已有内容
- 保持不变

### 3. confirm 后再写库

写库动作应该复用统一的 confirm/cancel 主链，而不是再做一个隐式 apply。

这能保证：

- UI 有明确 review 边界
- 数据写入能被审计
- Agent 下次对话时可以优先信任数据库真值

进一步的工程收口建议是：

- `apply` 边界本身也要有最小 runtime contract
- 至少明确拒绝：
  - 空的 `proposed_changes`
  - 缺少 `field_key`
  - 不支持的 delta `mode`

不要把这些假设只留给“调用方应该先 preview 过”。  
真正进入写库的方法，应该自己守住最后一道边界。

### 4. 对象级写回必须落到对象级存储

如果提议的上下文是“当前产品 / 当前客户 / 当前线程”的专属信息，就不能偷懒写进用户级共享 fallback store。

典型错误是：

- UI 让用户以为自己在改“这个产品”的首触达骨架
- 实际实现却把它写进“用户 + 语言”的共享模板

这会导致：

- 改 A 对象时无意覆盖 B 对象
- Agent 下次在别的对象里读到错误的共享值
- portfolio / readiness / family grouping 都被污染

更稳的做法是：

- 对象级字段优先落到对象自己的数据模型
- 历史共享模板只作为 read fallback
- readiness / summary / observability 全部优先读对象真值，再回退到共享默认值

## 为什么有效

- 把“Agent 看起来懂了”变成“系统真的记住了”
- 把高熵聊天输入压成低熵字段变更
- 避免 generic chat 直接拥有高风险写权限
- 让后续 Agent 对话能自然地区分“新增”与“更新”

## 适用场景

- 产品资料补全
- 账户/客户/机会上下文收集
- 模板骨架与商业默认值建议
- 任何“聊天收集上下文 -> 系统记住 -> 后续继续使用”的 Agent 工作流

## 反模式

- 把 generic Agent 直接接到数据库写操作
- 不读旧值就让 Agent 猜这是新增还是更新
- 把 review 做成另一个独立页面，迫使用户来回跳转
- 把对象级上下文写进用户级共享模板或共享配置，再假装它是对象专属状态

## 来源

TradeRadar `Phase 28AQ`：把 generic Agent 的产品上下文补充收口成 `review-before-write`，并让 `LaunchInterview` 与 free-form chat 共用“existing value / add vs update”语义。

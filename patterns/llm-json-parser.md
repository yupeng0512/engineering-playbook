# Pattern: LLM JSON 清洗

> 来源项目: InfoHunter | 推荐指数: 5/5 | 适用范围: 任何需要从 LLM 输出中提取结构化 JSON 的场景

## 适用场景

- AI Agent 输出 JSON 格式的分析结果
- 需要 LLM 返回结构化数据（评分、分类、摘要等）
- prompt 中要求纯 JSON 输出但 LLM 不一定遵循

## 问题根因

即使 prompt 中明确要求"纯 JSON 输出，不要 markdown 标记"，LLM 仍会概率性出现：

1. 用 \`\`\`json ... \`\`\` 包裹
2. JSON 前后有解释文字
3. 使用单引号而非双引号
4. 尾部有多余的逗号
5. 字符串中包含未转义的换行符

## 核心实现

```python
import re
import json

def fix_json_value(raw: str) -> dict | None:
    """多层 fallback 的 LLM JSON 清洗"""
    if not raw or not raw.strip():
        return None

    text = raw.strip()

    # Layer 1: 去掉 markdown 代码块包裹
    if text.startswith("```"):
        lines = text.split("\n")
        # 去掉第一行 (```json) 和最后一行 (```)
        lines = [l for l in lines[1:] if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()

    # Layer 2: 直接尝试解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Layer 3: 截断 JSON 结束后的多余文本
    # 找到最后一个 } 的位置
    last_brace = text.rfind("}")
    if last_brace > 0:
        try:
            return json.loads(text[: last_brace + 1])
        except json.JSONDecodeError:
            pass

    # Layer 4: 用 regex 提取 JSON 对象
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Layer 5: 尝试修复单引号
    try:
        fixed = text.replace("'", '"')
        return json.loads(fixed)
    except (json.JSONDecodeError, Exception):
        pass

    return None
```

## 前后对比

| 维度 | 无清洗层 | 有清洗层 |
|------|---------|---------|
| 解析成功率 | ~70-80% | ~95%+ |
| 失败处理 | 直接报错丢弃 | 多层 fallback 尽力恢复 |
| 可维护性 | 每次遇到新格式改 prompt | 在 parser 层统一处理 |

## 使用注意事项

1. 清洗层是"最后防线"，prompt 端仍应尽量要求纯 JSON 输出
2. 考虑记录清洗命中了哪一层，用于统计 LLM 遵循率
3. 对于高可靠性场景，可结合 Pydantic model 做 schema 校验

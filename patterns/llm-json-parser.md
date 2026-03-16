---
title: llm-json-parser
type: note
permalink: engineering-playbook/patterns/llm-json-parser
---

# Pattern: LLM JSON 清洗

> 来源项目: InfoHunter, truthsocial-trump-monitor, next-ai-draw-io
> 推荐指数: 5/5 | 适用范围: 任何需要从 LLM 输出中提取结构化 JSON 的场景
> 门控审核: 2026-02-25（修复 Layer 5 单引号 bug，新增 trailing comma 和数组支持）

## 适用场景

- AI Agent 输出 JSON 格式的分析结果
- 需要 LLM 返回结构化数据（评分、分类、摘要等）
- prompt 中要求纯 JSON 输出但 LLM 不一定遵循

## 问题根因

即使 prompt 中明确要求"纯 JSON 输出，不要 markdown 标记"，LLM 仍会概率性出现：

1. 用 \`\`\`json ... \`\`\` 包裹
2. JSON 前后有解释文字
3. 使用单引号而非双引号（但值中可能有英文撇号如 `O'Brien`）
4. 尾部有多余的逗号 `{..., }`
5. 字符串中包含未转义的换行符
6. 返回数组 `[...]` 而非对象 `{...}`

## 核心实现

```python
import re
import json
import ast

def fix_json_value(raw: str) -> dict | list | None:
    """多层 fallback 的 LLM JSON 清洗"""
    if not raw or not raw.strip():
        return None

    text = raw.strip()

    # Layer 1: 去掉 markdown 代码块包裹
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines[1:] if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()

    # Layer 2: 直接尝试解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Layer 3: 截断 JSON 结束后的多余文本
    last_brace = text.rfind("}")
    last_bracket = text.rfind("]")
    last_end = max(last_brace, last_bracket)
    if last_end > 0:
        try:
            return json.loads(text[: last_end + 1])
        except json.JSONDecodeError:
            pass

    # Layer 4: 用 regex 提取 JSON 对象或数组
    for pattern in [r"\{[\s\S]*\}", r"\[[\s\S]*\]"]:
        match = re.search(pattern, text)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

    # Layer 5: 修复 trailing comma（{..., } → {...}）
    cleaned = re.sub(r',\s*([}\]])', r'\1', text)
    if cleaned != text:
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

    # Layer 6: 修复单引号（用 ast.literal_eval 安全处理，不破坏 O'Brien 类值）
    try:
        result = ast.literal_eval(text)
        if isinstance(result, (dict, list)):
            return result
    except (ValueError, SyntaxError):
        pass

    return None
```

## 前后对比

| 维度 | 无清洗层 | 有清洗层 |
|------|---------|---------|
| 解析成功率 | ~70-80% | ~95%+ |
| 失败处理 | 直接报错丢弃 | 6 层 fallback 尽力恢复 |
| 可维护性 | 每次遇到新格式改 prompt | 在 parser 层统一处理 |

## 测试用例

```python
# 正常 JSON
assert fix_json_value('{"score": 8}') == {"score": 8}

# Markdown 包裹
assert fix_json_value('```json\n{"score": 8}\n```') == {"score": 8}

# 前后有解释文字
assert fix_json_value('Here is the result:\n{"score": 8}\nDone.') == {"score": 8}

# Trailing comma
assert fix_json_value('{"a": 1, "b": 2, }') == {"a": 1, "b": 2}

# 单引号（含撇号安全）
assert fix_json_value("{'name': \"O'Brien\", 'score': 8}") == {"name": "O'Brien", "score": 8}

# 数组返回
assert fix_json_value('[{"id": 1}, {"id": 2}]') == [{"id": 1}, {"id": 2}]
```

## 使用注意事项

1. 清洗层是"最后防线"，prompt 端仍应尽量要求纯 JSON 输出
2. 考虑记录清洗命中了哪一层，用于统计 LLM 遵循率
3. 对于高可靠性场景，可结合 Pydantic model 做 schema 校验
4. 更深度的场景（中日韩引号归一化、字符级状态机修复未转义双引号），参考 InfoHunter 的 `agui_client.py` 实现
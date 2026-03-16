---
name: unittest
description: 单元测试助手（通用版）。当用户表达"运行单测"、"执行单测"、"单元测试"、"跑测试"、"测试用例"、"写单测"、"添加测试"、"TDD"、"测试驱动"、"红绿重构"等意图时触发。支持执行、编写和调试单元测试，强制遵循
  TDD 红-绿-重构循环。适用于 Python（pytest/unittest）、Django、以及其他测试框架。
permalink: engineering-playbook/skills/personal/unittest/skill
---

# 单元测试助手（通用版）

你是单元测试专家，负责执行、编写和调试单元测试。**必须遵循 TDD（测试驱动开发）方法论，强制执行红-绿-重构循环。**

---

## 0. TDD 强制工作流

### 0.1 核心原则

**测试优先，验证收尾**：任何代码变更必须先有测试，完成前必须验证测试通过。

```
┌─────────────────────────────────────────────────────────────────┐
│                    TDD 红-绿-重构循环                            │
├─────────────────────────────────────────────────────────────────┤
│  🔴 RED      →    🟢 GREEN    →    🔵 REFACTOR    →    ✅ VERIFY │
│  写失败测试       写最小实现       优化代码结构        验证通过    │
└─────────────────────────────────────────────────────────────────┘
```

### 0.2 强制执行规则

| 规则 | 说明 | 违反后果 |
|------|------|----------|
| **测试先行** | 新功能/Bug 修复必须先写测试 | 代码不会被接受 |
| **失败优先** | 新测试必须先失败（验证测试有效性） | 测试可能无效 |
| **最小实现** | 只写让测试通过的最少代码 | 避免过度设计 |
| **验证收尾** | 任务完成前必须运行测试验证 | 不验证不算完成 |

### 0.3 TDD 工作流详解

#### 🔴 Phase 1: RED（写失败的测试）

编写一个能清晰描述预期行为的测试，确保它会失败。

```python
def test_calculate_discount_for_vip_user():
    """VIP 用户应该获得 20% 折扣"""
    # Arrange
    user = User(level="vip")
    order = Order(amount=100)

    # Act
    discount = calculate_discount(user, order)

    # Assert
    assert discount == 20
```

**执行验证**（必须）：运行测试，预期失败。如果通过，说明测试无效。

#### 🟢 Phase 2: GREEN（写最小实现）

编写让测试通过的最少代码，不追求完美。

#### 🔵 Phase 3: REFACTOR（优化代码）

在测试保护下优化代码结构，消除重复，提高可读性。验证所有测试仍通过。

#### ✅ Phase 4: VERIFY（完成验证）

运行完整测试套件，确认无新增失败。

### 0.4 测试反模式检查

| 反模式 | 症状 | 解决方案 |
|--------|------|----------|
| **无效断言** | `assert True`、`assert result` | 编写具体的断言条件 |
| **过度 Mock** | Mock 了被测代码本身 | 只 Mock 外部依赖 |
| **测试顺序依赖** | 单独运行失败，一起运行通过 | 每个测试独立 setUp/tearDown |
| **脆弱测试** | 时间/随机数导致不稳定 | Mock 时间，固定随机种子 |
| **测试过大** | 一个测试验证多个行为 | 拆分为多个专注的测试 |
| **缺少边界测试** | 只测试 Happy Path | 添加边界条件和异常测试 |
| **硬编码数据** | 测试数据散落各处 | 集中管理测试数据 |

### 0.5 任务完成检查清单

**在报告任务完成之前，必须确认**：

- [ ] 新增功能有对应测试
- [ ] Bug 修复有回归测试
- [ ] 边界条件已测试
- [ ] 异常场景已测试
- [ ] 测试命名遵循 `test_{method}_{scenario}` 格式
- [ ] 每个测试遵循 AAA 模式
- [ ] 每个测试有清晰的文档字符串
- [ ] 🔴 RED → 🟢 GREEN → 🔵 REFACTOR → ✅ VERIFY 全部完成

---

## 1. 环境自适应

启动时需确认项目的测试环境：

| 配置项 | 需要确认 |
|--------|----------|
| 测试框架 | pytest / unittest / Jest / 其他 |
| 运行命令 | 项目的测试执行命令 |
| 虚拟环境 | Python 虚拟环境路径（如有） |
| 配置文件 | pytest.ini / setup.cfg / pyproject.toml 等 |

如果项目根目录有 `pytest.ini`、`pyproject.toml`（含 `[tool.pytest]`）或 `setup.cfg`（含 `[tool:pytest]`），使用 pytest。否则询问用户。

---

## 2. 编写单测规范

### 2.1 AAA 模式（Arrange-Act-Assert）

**所有测试必须遵循 AAA 模式**：

```python
def test_create_policy_success():
    """测试成功创建策略"""
    # Arrange - 准备测试数据和模拟对象
    policy_data = {"name": "测试策略", "type": "approval"}

    # Act - 执行被测试的方法
    policy = PolicyService.create(**policy_data)

    # Assert - 验证结果和行为
    assert policy.name == "测试策略"
    assert policy.id is not None
```

### 2.2 测试命名规范

**格式**: `test_{方法名}_{场景描述}`

| 场景 | 命名示例 |
|------|----------|
| 成功场景 | `test_create_policy_success` |
| 缺少参数 | `test_execute_missing_required_params` |
| 参数类型错误 | `test_execute_invalid_type_params` |
| 处理器异常 | `test_execute_handler_exception` |

### 2.3 测试优先级

1. **Happy Path** — 核心正常流程
2. **边界条件** — 空值、极限值、边界值
3. **异常场景** — 错误输入、外部依赖故障
4. **回归测试** — Bug 修复后的防护测试

### 2.4 测试独立性

- 每个测试必须独立运行，不依赖其他测试的状态
- 不能有测试执行顺序依赖
- 使用 setUp/tearDown 确保数据隔离

---

## 3. Mock 策略

### 3.1 Mock 决策原则

| 场景 | 是否 Mock | 说明 |
|------|-----------|------|
| 外部 API 调用 | ✅ 必须 Mock | 避免网络依赖 |
| 第三方服务 | ✅ 必须 Mock | 保证测试可重复 |
| 数据库操作 | 视情况 | 简单查询可用测试数据库 |
| 内部纯函数 | ❌ 不需要 | 数据转换、计算逻辑 |
| 时间相关 | ✅ 建议 Mock | 保证测试可重复 |

### 3.2 Mock 最佳实践

```python
from unittest.mock import patch, MagicMock, Mock

# 推荐：使用 spec 确保 Mock 对象有正确的接口
mock_repository = Mock(spec=UserRepository)

# 使用 patcher 模式，确保 tearDown 时清理
class TestMyService(TestCase):
    def setUp(self):
        self.patcher = patch("mymodule.ExternalAPI")
        self.mock_api = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
```

---

## 4. Django 数据库测试（如适用）

```python
import pytest

# 单个测试
@pytest.mark.django_db
def test_create_model():
    pass

# 整个测试类
@pytest.mark.django_db
class TestMyModel:
    pass
```

---

## 5. 断言质量要求

- 每个测试必须至少包含一个有效断言
- 断言失败必须能明确指示失败原因
- 避免无意义的断言（如 `assert True`）

```python
# 数值断言
assert result.count == 5

# 对象断言
assert isinstance(result, User)
assert result.username == "expected_username"

# 异常断言
with pytest.raises(ValueError) as exc_info:
    service.validate_email("invalid-email")
assert "Invalid email" in str(exc_info.value)

# Mock 断言
mock_repo.create.assert_called_once_with(expected_data)
```

---

## 6. 参数化测试

```python
@pytest.mark.parametrize("status,expected", [
    ("active", "启用"),
    ("disabled", "停用"),
    ("pending", "待审"),
])
def test_status_display(status, expected):
    """测试状态显示"""
    obj = MyModel(status=status)
    assert obj.get_status_display() == expected
```

---

## 7. Fixture 使用规范

```python
# function 级别（默认）- 每个测试函数执行一次
@pytest.fixture
def user():
    return User.objects.create(username="test")

# 带清理的 fixture
@pytest.fixture
def temp_file():
    path = create_temp_file()
    yield path
    os.unlink(path)
```

---

## 8. 常见问题排查

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 测试结果不稳定 | 测试顺序依赖 / 时间相关断言 | 确保独立性 / Mock 时间 |
| Import 错误 | 工作目录不对 / sys.path 缺失 | 确保在项目根目录执行 |
| 数据库访问错误 | 缺少 `@pytest.mark.django_db` | 添加装饰器 |
| Mock 不生效 | patch 路径不对 | patch 导入路径而非定义路径 |

---

## 任务执行

根据用户需求执行对应操作：

1. **执行测试**：确认运行命令和范围，在终端执行
2. **编写测试**：**必须遵循 TDD 红-绿-重构循环**
3. **调试测试**：使用调试参数定位问题

**禁止行为**：
- ❌ 先写实现再补测试
- ❌ 跳过测试失败验证
- ❌ 不运行测试就报告完成
- ❌ 忽略测试反模式
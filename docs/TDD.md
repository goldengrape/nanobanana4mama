
# 测试设计文档 (TDD): “AI亲情画板”项目

| 文档版本 | 创建日期 | 关联文档 |
| :--- | :--- | :--- |
| v1.0 | 2025年9月3日 | `模块设计文档 (MDD) v1.0` |

-----

## 1\. 文档引言

### 1.1 目的

本测试设计文档（TDD）旨在为“AI亲情画板”项目的单元测试阶段提供一个全面的、可执行的测试计划。本文档基于`MDD v1.0`中定义的模块和接口，设计了一系列测试用例，以验证各个模块功能的正确性、稳定性和鲁棒性。

### 1.2 测试范围

#### 范围内 (In-Scope):

  - 对 `auth_module.py` 的单元测试。
  - 对 `gemini_api_module.py` 的单元测试。
  - 测试将聚焦于模块的公共接口、业务逻辑和边界条件。

#### 范围外 (Out-of-Scope):

  - **UI层测试**: `app.py` 模块与Streamlit的UI渲染和状态管理紧密耦合，不适合进行传统的单元测试。其正确性将通过集成测试和手动测试来保证。
  - **端到端 (E2E) 测试**: 模拟完整用户行为流程的测试。
  - **性能测试**: API响应时间、应用加载速度等性能指标的测试。

### 1.3 测试框架与工具

  - **测试框架**: `pytest`
  - **辅助工具**:
      - `pytest-mock`: 用于模拟（Mock）外部依赖，如文件系统访问和API网络请求。
      - `Pillow` (PIL): 用于验证图像对象的创建和类型。

-----

## 2\. 测试环境

  - **Python版本**: `3.9+`
  - **操作系统**: 不限 (Windows, macOS, Linux)
  - **核心依赖**: `streamlit`, `streamlit-authenticator`, `google-generativeai`, `pytest`, `pytest-mock`, `pillow`

-----

## 3\. 测试用例设计

### 3.1 认证模块 (`auth_module.py`)

  - **被测对象**: `get_authenticator()` 函数
  - **测试策略**: 重点测试函数对 `secrets.toml` 配置文件的依赖性，包括正常和异常情况。

| 测试用例ID | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
| :--- | :--- | :--- | :--- | :--- |
| **TC-AUTH-001** | **成功场景** - 配置文件完整且正确 | 模拟一个包含有效`[credentials]`和`[cookie]`节的`secrets.toml`文件。 | 1. 调用 `get_authenticator()`。 | 1. 函数成功返回一个`Authenticate`对象实例。\<br\>2. 不抛出任何异常。 |
| **TC-AUTH-002** | **失败场景** - 配置文件不存在 | 模拟 `open()` 函数抛出 `FileNotFoundError`。 | 1. 调用 `get_authenticator()`。 | 1. 函数向上抛出 `FileNotFoundError` 异常。 |
| **TC-AUTH-003** | **失败场景** - 缺少`[credentials]`节 | 模拟的`secrets.toml`文件中不包含`[credentials]`节。 | 1. 调用 `get_authenticator()`。 | 1. 函数因配置不完整而抛出 `KeyError` 或类似的配置错误异常。 |
| **TC-AUTH-004** | **失败场景** - 缺少`[cookie]`节 | 模拟的`secrets.toml`文件中不包含`[cookie]`节。 | 1. 调用 `get_authenticator()`。 | 1. 函数因配置不完整而抛出 `KeyError` 或类似的配置错误异常。 |

### 3.2 AI服务模块 (`gemini_api_module.py`)

  - **被测对象**: `generate_image_from_conversation()` 函数
  - **测试策略**: 采用Mocking技术隔离对Google Gemini API的真实网络请求。重点测试API请求的构建、响应的解析、上下文窗口逻辑以及各种错误处理。

| 测试用例ID | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
| :--- | :--- | :--- | :--- | :--- |
| **TC-API-001** | **成功场景** - API成功返回图片 | 1. Mock Gemini API客户端使其返回一个有效的、包含base64编码图片数据的响应。\<br\>2. 准备一个有效的`conversation_history`列表。 | 1. 调用 `generate_image_from_conversation()`。 | 1. 函数返回一个有效的 `PIL.Image.Image` 对象。\<br\>2. 不抛出异常。 |
| **TC-API-002** | **失败场景** - API返回错误信息 | 1. Mock Gemini API客户端使其返回一个错误状态或包含错误信息的响应。 | 1. 调用 `generate_image_from_conversation()`。 | 1. 函数捕获API错误并抛出自定义的 `APIError` 异常。 |
| **TC-API-003** | **失败场景** - 发生网络错误 | 1. Mock Gemini API客户端在调用时抛出网络相关的异常（如 `ConnectionError`）。 | 1. 调用 `generate_image_from_conversation()`。 | 1. 函数在重试后依然失败，并最终抛出自定义的 `NetworkError` 异常。 |
| **TC-API-004** | **逻辑验证** - 上下文窗口切片正确 | 1. 准备一个长度大于`context_window`（例如10条）的`conversation_history`。\<br\>2. 设定 `context_window` 为6。\<br\>3. Mock Gemini API客户端。 | 1. 调用 `generate_image_from_conversation()`。 | 1. 断言（Assert）传递给Mock API客户端的对话历史列表的长度正好等于`context_window`（即6）。\<br\>2. 断言传递的内容是原始历史记录的最后6条。 |
| **TC-API-005** | **边界场景** - 对话历史为空 | 1. 传入一个空的`conversation_history`列表。 | 1. 调用 `generate_image_from_conversation()`。 | 1. 函数应处理此情况，例如抛出 `ValueError` 或返回 `None`（具体行为需在函数内定义）。 |
| **TC-API-006** | **边界场景** - `context_window`为0或负数 | 1. 传入 `context_window = 0`。 | 1. 调用 `generate_image_from_conversation()`。 | 1. 函数应抛出 `ValueError` 异常，因为前置条件要求其为正整数。 |

-----

## 4\. 测试执行

### 4.1 执行命令

在项目的根目录下，运行以下命令来执行所有测试：

```bash
pytest
```
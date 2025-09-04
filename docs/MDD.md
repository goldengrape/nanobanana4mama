
# 模块设计文档 (MDD): “AI亲情画板”项目

| 文档版本 | 创建日期 | 关联文档 |
| :--- | :--- | :--- |
| v1.0 | 2025年9月3日 | `公理设计文档 (ADD) v1.0`, `用户需求文档 (URD) v1.1` |

-----

## 1\. 文档引言

### 1.1 目的

本模块设计文档（MDD）旨在为“AI亲情画板”项目提供一个清晰、可执行的软件模块级设计方案。本文档是`ADD v1.0`的具体化，将设计参数（DPs）转化为明确的模块、接口和数据结构，以指导后续的编码工作。

### 1.2 设计原则

  - **奥卡姆剃刀原则 (Occam's Razor):** "如无必要，勿增实体"。本设计将避免过度工程化，以最少的模块和最简洁的接口满足MVP（最小可行产品）的全部需求。
  - **契约式编程原则 (Design by Contract):** 每个模块的公开接口（函数）都将明确其契约，包括前置条件、后置条件和不变式，以确保模块间的交互是可靠和可预测的。

-----

## 2\. 系统架构概览

根据奥卡姆剃刀原则，我们将整个应用划分为三个核心逻辑模块，并由一个主应用文件进行调度。

  - **主应用 (`app.py`):** 作为应用的入口和UI渲染层，负责整体流程控制。
  - **认证模块 (`src/auth_module.py`):** 封装所有与用户身份验证和会话管理相关的逻辑。
  - **AI服务模块 (`src/gemini_api_module.py`):** 封装所有与Google Gemini API (Nano Banana) 交互的逻辑。

### 2.1 模块交互图

```text
+--------------------------------+
|         用户 (浏览器)          |
+--------------------------------+
             |
             v
+--------------------------------+       +--------------------------------+
|      主应用 (app.py)           |------>|     认证模块 (auth_module.py)    |
| - UI 渲染与状态管理 (st)        |       | - 初始化 authenticator         |
| - 调度核心逻辑                  |       | - 执行登录/登出                |
+--------------------------------+       +--------------------------------+
             |
             v
+--------------------------------+
|   AI服务模块 (gemini_api.py)     |
| - 构建 API 请求                 |
| - 调用 Gemini API (HTTP)       |
| - 处理 API 响应 (解码图片)       |
| - 错误处理与重试                |
+--------------------------------+
```

-----

## 3\. 模块详细设计

### 3.1 认证模块 (`src/auth_module.py`)

  - **目的:** 隔离并统一处理用户认证、凭证管理和会话Cookie。
  - **依赖:** `streamlit-authenticator`, `streamlit`, `PyYAML`
  - **公开接口 (API):**
    ```python
    def get_authenticator() -> Authenticate:
        """
        初始化并返回一个配置好的 streamlit-authenticator 实例。
        这是该模块唯一的公开函数。
        """
        # --- 契约 ---
        # 前置条件: 
        #   - .streamlit/secrets.toml 文件必须存在。
        #   - secrets.toml 中必须包含 [credentials] 部分，且格式符合 authenticator 的要求。
        #   - secrets.toml 中必须包含 [cookie] 部分，用于配置Cookie。
        # 后置条件: 
        #   - 成功: 返回一个功能完备的 Authenticate 对象。
        #   - 失败: 向上抛出 FileNotFoundError 或 KeyError 异常。
    ```

### 3.2 AI服务模块 (`src/gemini_api_module.py`)

  - **目的:** 封装与Google Gemini API的所有交互，对上层应用屏蔽API的具体细节。
  - **依赖:** `streamlit`, `google-generativeai`, `PIL`
  - **公开接口 (API):**
    ```python
    def generate_image_from_conversation(
        api_key: str, 
        conversation_history: list, 
        context_window: int
    ) -> Image.Image:
        """
        根据对话历史，调用 Gemini API (gemini-2.5-flash-image-preview) 生成一张图片。
        """
        # --- 契约 ---
        # 前置条件:
        #   - api_key (str): 必须是有效的Google API密钥。
        #   - conversation_history (list): 必须是一个列表，其中每个元素是符合Gemini API格式的字典
        #     （如 {"role": "user", "parts": [{"text": "..."}]}）。
        #   - context_window (int): 必须是一个正整数。
        # 后置条件:
        #   - 成功: 返回一个 PIL.Image.Image 对象。
        #   - 失败: 
        #     - 如果API返回错误或响应格式不正确，抛出自定义的 APIError 异常。
        #     - 如果发生网络问题且重试后依然失败，抛出自定义的 NetworkError 异常。
    ```

### 3.3 主应用模块 (`app.py`)

  - **目的:** 作为应用的入口，集成其他模块，渲染UI，并管理会话状态。
  - **依赖:** `streamlit`, `auth_module.py`, `gemini_api_module.py`
  - **核心逻辑:**
    1.  **初始化:**
          - 设置页面配置 (`st.set_page_config`)。
          - 调用 `auth_module.get_authenticator()` 获取认证器实例。
          - 执行认证器的登录流程 (`authenticator.login()`)。
    2.  **认证状态检查:**
          - `if st.session_state["authentication_status"]:` 用户已登录。
              - 渲染欢迎信息和登出按钮。
              - 执行核心的图片生成应用逻辑。
          - `elif st.session_state["authentication_status"] is False:` 认证失败。
              - 使用 `st.error` 显示错误信息。
          - `elif st.session_state["authentication_status"] is None:` 等待登录。
              - 使用 `st.warning` 显示提示信息。
    3.  **核心应用逻辑 (登录后):**
          - **状态初始化:** 检查 `st.session_state` 中是否存在 `messages` 列表，如果不存在则创建它。
          - **UI渲染:**
              - 使用 `st.chat_message` 遍历并显示 `st.session_state.messages` 中的历史记录。
              - 使用 `st.chat_input` 提供用户输入框。
              - 在侧边栏或主页底部，使用 `st.button` 渲染“重新开始”和快捷指令按钮。
              - 如果当前有图片，则使用 `st.image` 显示，并使用 `st.download_button` 提供下载。
          - **逻辑处理:**
              - 当用户提交输入时，将新消息追加到 `st.session_state.messages`。
              - 从 `st.secrets` 读取 `api_key` 和 `context_window`。
              - 调用 `gemini_api_module.generate_image_from_conversation()` 并传入所需参数。
              - 使用 `st.spinner` 显示加载状态。
              - 处理返回的图片或异常。
              - 将AI的返回（图片和可能的文本）也存入 `st.session_state.messages` 并刷新页面。

-----

## 4\. 数据模型设计

本应用的核心数据模型将完全依赖Streamlit的 `st.session_state` 对象进行管理。

  - `st.session_state.authentication_status`: (`bool | None`) 由 `streamlit-authenticator` 库管理，用于跟踪用户的登录状态。
  - `st.session_state.name`: (`str`) 由 `streamlit-authenticator` 管理，存储当前登录用户的显示名称。
  - `st.session_state.username`: (`str`) 由 `streamlit-authenticator` 管理，存储当前登录用户的用户名。
  - `st.session_state.messages`: (`list`) 由本应用管理。这是核心的对话历史记录。列表中的每个元素都是一个字典，结构如下：
    ```json
    {
      "role": "user" | "model",
      "content": "..." 
    }
    ```
    **注意:** `content` 对于用户是文本，对于模型可以是图片数据或文本。在传递给 `gemini_api_module` 之前，此结构需要被转换为符合Gemini API `contents` 字段的格式。

-----

## 5\. 结论

本MDD文档提供了一个简洁而完整的模块设计方案。通过将系统划分为三个高内聚、低耦合的模块，并为每个模块的接口定义了清晰的契约，我们为后续的开发工作奠定了坚实的基础。该设计遵循了奥卡姆剃刀原则，确保了MVP范围内的功能得以高效实现，同时具备良好的可读性和可维护性。
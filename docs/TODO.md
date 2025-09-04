
# “AI亲情画板”项目开发 TODO List

这是一个从零开始到完成部署的完整工作流程。请按顺序完成每个阶段的任务。

-----

## 阶段一：项目初始化与环境设置 (Phase 1: Setup)

  - [x] **1. 创建项目结构:**
      - [x] 在您的电脑上创建主项目文件夹 `ai-family-palette/`。
      - [x] 在主文件夹内，创建我们设计的全部目录和空的`.py`文件：
        ```bash
        mkdir .streamlit
        mkdir src
        mkdir tests
        touch .streamlit/secrets.toml.template
        touch src/__init__.py
        touch src/auth_module.py
        touch src/gemini_api_module.py
        touch tests/__init__.py
        touch tests/test_auth_module.py
        touch tests/test_gemini_api_module.py
        touch app.py
        touch .gitignore
        touch README.md
        ```
  - [ ] **2. 配置Python环境:**
      - [x] 在项目根目录下，将我们之前生成的 `pyproject.toml` 文件放进去。
      - [ ] 运行 `poetry install` 来创建虚拟环境并安装所有核心依赖和开发依赖。
      - [ ] 激活虚拟环境 (运行 `poetry shell`)。
  - [ ] **3. 配置机密文件:**
      - [ ] 复制 `.streamlit/secrets.toml.template` 并重命名为 `.streamlit/secrets.toml`。
      - [ ] 在 `.streamlit/secrets.toml` 文件中填入您的真实Google API Key和预设的用户信息。
      - [x] **【重要】** 在 `.gitignore` 文件中加入 `.streamlit/secrets.toml` 和 `unit-test-result.txt`，确保它们不会被上传到代码仓库。

-----

## 阶段二：核心模块开发 (Phase 2: Core Logic - Test-Driven)

在这个阶段，我们将遵循TDD（测试驱动开发）的理念：先写测试，再写代码让测试通过。

  - [ ] **4. 开发AI服务模块:**
      - [ ] **编写测试:** 打开 `tests/test_gemini_api_module.py`，根据我们的TDD文档，编写所有针对`generate_image_from_conversation`函数的测试用例（成功、失败、边界情况等）。此时运行 `pytest` 会看到所有测试失败。
      - [ ] **编写功能代码:** 打开 `src/gemini_api_module.py`，实现 `generate_image_from_conversation` 函数的逻辑。
      - [ ] **运行测试:** 反复运行 `pytest`，直到 `test_gemini_api_module.py` 中的所有测试都通过。
  - [ ] **5. 开发认证模块:**
      - [ ] **编写测试:** 打开 `tests/test_auth_module.py`，根据TDD文档，为`get_authenticator`函数编写测试用例。
      - [ ] **编写功能代码:** 打开 `src/auth_module.py`，实现 `get_authenticator` 函数。
      - [ ] **运行测试:** 运行 `pytest`，确保 `test_auth_module.py` 中的所有测试都通过。

-----

## 阶段三：UI集成与应用实现 (Phase 3: Integration)

现在我们有了经过测试的核心模块，可以开始构建用户界面了。

  - [ ] **6. 撰写主应用 `app.py`:**
      - [ ] **集成认证:** 在 `app.py` 中，导入并使用 `auth_module` 来创建登录页面和检查用户登录状态。
      - [ ] **构建UI框架:** 根据MDD文档，使用Streamlit组件 (`st.chat_message`, `st.chat_input`, `st.button` 等) 搭建出对话界面的基本框架。
      - [ ] **管理会话状态:** 使用 `st.session_state` 来初始化和管理对话历史 (`messages`)。
      - [ ] **连接AI服务:** 在用户输入后，调用 `gemini_api_module` 中的函数来获取AI生成的图片。
      - [ ] **实现完整流程:** 将加载提示、图片显示、图片下载、对话历史更新、错误处理等所有逻辑串联起来。
      - [ ] **本地调试:** 在这个阶段，您会频繁地在终端运行 `streamlit run app.py`，在浏览器中查看和调试您的应用。

-----

## 阶段四：文档与部署准备 (Phase 4: Finalization)

项目功能完成，我们开始准备将其开源并部署。

  - [ ] **7. 撰写文档 (`README.md`):**
      - [ ] 详细描述这个项目是做什么的，它的目标用户是谁。
      - [ ] 提供清晰的本地运行指南：如何克隆项目、如何安装依赖、如何配置 `secrets.toml`。
      - [ ] 解释如何部署到Streamlit Cloud。
      - [ ] 提及API成本风险。
  - [ ] **8. 生成部署文件 (`requirements.txt`):**
      - [ ] 在终端运行 `poetry export -f requirements.txt --output requirements.txt --without-hashes`。这会根据 `pyproject.toml` 生成Streamlit Cloud部署所需的 `requirements.txt` 文件。
  - [ ] **9. 代码审查与清理:**
      - [ ] 回顾所有代码，添加必要的注释，删除无用的测试代码。
      - [ ] 确保代码风格一致。

-----

## 阶段五：部署 (Phase 5: Deployment)

  - [ ] **10. 上传到GitHub:**
      - [ ] 创建一个新的GitHub仓库。
      - [ ] 将您的本地项目（除了`.gitignore`中忽略的文件）推送到这个仓库。
  - [ ] **11. 部署到Streamlit Cloud:**
      - [ ] 登录您的Streamlit Cloud账户。
      - [ ] 从您的GitHub仓库新建一个应用。
      - [ ] **【重要】** 在Streamlit Cloud的“Advanced settings”中，将您的`secrets.toml`文件内容粘贴进去。
      - [ ] 点击“Deploy\!”，等待应用部署完成。
  - [ ] **12. 最终测试:**
      - [ ] 在部署好的线上应用中，亲自走一遍所有用户流程，确保一切正常。
      - [ ] 把链接和账号发给您的妈妈！🎉
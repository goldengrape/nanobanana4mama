import streamlit as st
import os
from datetime import datetime
from PIL import Image
import io
import base64

from src.auth_module import authenticate_user, UserNotFoundError, InvalidCredentialsError
from src.gemini_api_module import generate_image_from_conversation, APIError, NetworkError

# 页面配置
st.set_page_config(
    page_title="AI亲情画板",
    page_icon="👨‍👩‍👧‍👦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化会话状态
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'generated_images' not in st.session_state:
    st.session_state.generated_images = []

def login_page():
    """登录页面"""
    st.title("👨‍👩‍👧‍👦 AI亲情画板")
    st.markdown("### 用AI记录每一个温馨的亲情时刻")
    
    with st.form("login_form"):
        username = st.text_input("用户名", placeholder="请输入用户名")
        password = st.text_input("密码", type="password", placeholder="请输入密码")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("登录", use_container_width=True)
        
        if submitted:
            try:
                if authenticate_user(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.rerun()
            except UserNotFoundError:
                st.error("用户不存在，请检查用户名")
            except InvalidCredentialsError:
                st.error("密码错误，请重试")
            except ValueError as e:
                st.error(str(e))
    
    st.info("💡 提示：使用演示账号 - 用户名: demo_user, 密码: demo123")

def main_app():
    """主应用页面"""
    st.title("🎨 AI亲情画板")
    st.markdown(f"欢迎回来，{st.session_state.username}！让我们一起创造美好的亲情回忆")
    
    # 侧边栏
    with st.sidebar:
        st.header("📝 对话记录")
        
        # 清除对话按钮
        if st.button("清除对话记录", use_container_width=True):
            st.session_state.conversation_history = []
            st.session_state.generated_images = []
            st.rerun()
        
        st.divider()
        
        # 显示对话历史
        if st.session_state.conversation_history:
            st.subheader("历史对话")
            for i, msg in enumerate(st.session_state.conversation_history):
                role = "👤 我" if msg["role"] == "user" else "🤖 AI"
                st.text(f"{role}: {msg['content']}")
                if i < len(st.session_state.conversation_history) - 1:
                    st.markdown("---")
        else:
            st.info("开始第一次对话吧！")
        
        st.divider()
        
        # 登出按钮
        if st.button("退出登录", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.session_state.conversation_history = []
            st.session_state.generated_images = []
            st.rerun()
    
    # 主内容区域
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("💬 对话区域")
        
        # 用户输入
        user_input = st.text_area(
            "分享你的亲情故事或心情：",
            placeholder="例如：今天妈妈给我做了我最喜欢的红烧肉...",
            height=100,
            key="user_input"
        )
        
        if st.button("生成AI图片", type="primary", use_container_width=True):
            if user_input:
                # 添加到对话历史
                st.session_state.conversation_history.append({
                    "role": "user",
                    "content": user_input
                })
                
                # 获取API密钥
                api_key = st.secrets.get("GEMINI_API_KEY", "")
                if not api_key:
                    st.error("⚠️ 请先在.secrets.toml中配置GEMINI_API_KEY")
                    return
                
                # 生成图片
                with st.spinner("AI正在为你创作图片..."):
                    try:
                        image = generate_image_from_conversation(
                            st.session_state.conversation_history,
                            api_key
                        )
                        
                        # 保存生成的图片
                        img_bytes = io.BytesIO()
                        image.save(img_bytes, format='PNG')
                        img_bytes.seek(0)
                        
                        st.session_state.generated_images.append({
                            "image": image,
                            "prompt": user_input,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                        
                        # 添加AI回复到对话历史
                        st.session_state.conversation_history.append({
                            "role": "assistant",
                            "content": f"已为你生成了一张关于'{user_input}'的图片"
                        })
                        
                        st.rerun()
                        
                    except NetworkError:
                        st.error("网络连接错误，请检查网络后重试")
                    except APIError as e:
                        st.error(f"AI服务错误：{str(e)}")
                    except Exception as e:
                        st.error(f"发生未知错误：{str(e)}")
            else:
                st.warning("请先输入你想要表达的内容")
    
    with col2:
        st.header("🖼️ 生成的图片")
        
        if st.session_state.generated_images:
            # 显示最新生成的图片
            latest = st.session_state.generated_images[-1]
            st.image(latest["image"], caption=f"生成时间：{latest['timestamp']}", use_column_width=True)
            
            # 下载按钮
            img_bytes = io.BytesIO()
            latest["image"].save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            st.download_button(
                label="下载图片",
                data=img_bytes,
                file_name=f"ai_family_memory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                mime="image/png",
                use_container_width=True
            )
        else:
            st.info("还没有生成任何图片，开始对话吧！")
        
        # 显示历史图片缩略图
        if len(st.session_state.generated_images) > 1:
            st.subheader("历史图片")
            cols = st.columns(3)
            for i, img_data in enumerate(st.session_state.generated_images[:-1][-6:]):
                with cols[i % 3]:
                    st.image(img_data["image"], use_column_width=True)

# 主应用逻辑
if not st.session_state.authenticated:
    login_page()
else:
    main_app()
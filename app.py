import streamlit as st
from google import genai
import datetime

# 页面配置
st.set_page_config(page_title="AI 咨询合伙人", page_icon="🤝", layout="wide")

# 初始化 Session State (状态记忆)
if 'chat_log' not in st.session_state:
    st.session_state.chat_log = [] # 存储对话列表
if 'usage_count' not in st.session_state:
    st.session_state.usage_count = 0

# 自定义样式
st.markdown("""
    <style>
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    .stButton button { width: 100%; border-radius: 8px; }
    .sidebar-content { background-color: #f8f9fa; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 侧边栏 ---
with st.sidebar:
    st.title("⚙️ 控制面板")
    api_key = st.text_input("Gemini API Key", type="password")
    model_name = st.selectbox("选择模型", ["gemini-2.0-flash", "gemini-2.5-pro"])
    
    st.divider()
    if st.button("🗑️ 清空对话重来"):
        st.session_state.chat_log = []
        st.session_state.usage_count = 0
        st.rerun()
    
    # 导出功能
    if st.session_state.chat_log:
        st.divider()
        full_text = f"# AI 咨询记录\n生成时间: {datetime.datetime.now()}\n\n"
        for msg in st.session_state.chat_log:
            role = "用户" if msg["role"] == "user" else "AI 专家"
            full_text += f"### {role}:\n{msg['content']}\n\n"
        
        st.download_button(
            label="📥 导出咨询结论 (Markdown)",
            data=full_text,
            file_name=f"Consulting_Result_{datetime.date.today()}.md",
            mime="text/markdown"
        )

# --- 主界面 ---
st.title("🤝 拉式思维：AI 咨询合伙人")
st.caption("逻辑：AI 通过不断追问来压榨信息，直到推导出客观最优解。")

# 如果对话还没开始，显示输入表单
if not st.session_state.chat_log:
    with st.expander("📝 填写背景信息开始咨询", expanded=True):
        f1, f2 = st.columns(2)
        field = f1.text_input("专业领域", "副业转型")
        goal = f2.text_input("最终目标", "寻找适合的副业项目")
        status = st.text_area("现状描述", placeholder="42岁，白天上班，晚上有空...")
        limits = st.text_area("限制条件", placeholder="不露脸，每月收益目标...")
        
        if st.button("🎯 开始第一轮深度诊断"):
            if not api_key:
                st.error("请填入 API Key")
            else:
                initial_prompt = f"领域：{field}\n目标：{goal}\n现状：{status}\n限制：{limits}"
                st.session_state.chat_log.append({"role": "user", "content": initial_prompt})
                # 标记需要生成回复
                st.session_state.needs_reply = True
                st.rerun()

# 展示聊天流
for message in st.session_state.chat_log:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 处理 AI 回复逻辑
if 'needs_reply' in st.session_state and st.session_state.needs_reply:
    try:
        client = genai.Client(api_key=api_key)
        # 系统指令确保“拉式”逻辑贯穿始终
        sys_instruction = "你是一个‘拉式提问’专家。在用户未说‘我想看最终方案’前，请通过分析盲点并追问来获取信息。每次提问不超过3个，保持专业深度。"
        
        # 将历史记录转换为 API 格式
        history_for_api = [{"role": m["role"], "parts": [{"text": m["content"]}]} for m in st.session_state.chat_log]
        
        with st.spinner("AI 正在深度思考..."):
            response = client.models.generate_content(
                model=model_name,
                contents=st.session_state.chat_log[-1]["content"], # 这里简单处理，Gemini SDK 支持更复杂的 Chat 会话
                config={"system_instruction": sys_instruction}
            )
            st.session_state.chat_log.append({"role": "assistant", "content": response.text})
            st.session_state.usage_count += 1
            del st.session_state.needs_reply
            st.rerun()
    except Exception as e:
        st.error(f"API 错误: {e}")

# 用户后续回复框
if st.session_state.chat_log and "needs_reply" not in st.session_state:
    if user_input := st.chat_input("输入你的回答或补充信息..."):
        st.session_state.chat_log.append({"role": "user", "content": user_input})
        st.session_state.needs_reply = True
        st.rerun()
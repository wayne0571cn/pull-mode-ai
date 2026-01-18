import streamlit as st
from google import genai
import datetime

# 1. 页面配置与标题
st.set_page_config(page_title="AI 咨询合伙人-稳健版", page_icon="🤝", layout="wide")

# 2. 初始化状态 (增加对表单内容的缓存)
if 'chat_log' not in st.session_state:
    st.session_state.chat_log = []
if 'usage_count' not in st.session_state:
    st.session_state.usage_count = 0

# --- 侧边栏 ---
with st.sidebar:
    st.title("⚙️ 控制面板")
    api_key = st.text_input("Gemini API Key", type="password")
    model_name = st.selectbox("选择模型", ["gemini-2.0-flash", "gemini-2.5-pro"])
    
    st.divider()
    if st.button("🗑️ 清空对话并重置"):
        st.session_state.chat_log = []
        st.session_state.usage_count = 0
        st.rerun()
    
    # 导出功能（防止网络断开导致记录丢失，随时可以导出）
    if st.session_state.chat_log:
        st.divider()
        full_text = f"# AI 咨询记录\n生成时间: {datetime.datetime.now()}\n\n"
        for msg in st.session_state.chat_log:
            role = "用户" if msg["role"] == "user" else "AI 专家"
            full_text += f"### {role}:\n{msg['content']}\n\n"
        
        st.download_button(
            label="📥 导出当前对话防止丢失",
            data=full_text,
            file_name=f"Consulting_Log_{datetime.date.today()}.md",
            mime="text/markdown"
        )

# --- 主界面 ---
st.title("🤝 拉式思维：AI 咨询合伙人")

# 初始表单部分 - 使用 key 参数确保内容在页面刷新时能保留在缓存里
if not st.session_state.chat_log:
    with st.expander("📝 第一步：填写背景信息开始咨询", expanded=True):
        f1, f2 = st.columns(2)
        field = f1.text_input("专业领域", value="副业转型", key="field_input")
        goal = f2.text_input("最终目标", value="寻找适合的副业项目", key="goal_input")
        status = st.text_area("现状描述", placeholder="例如：36岁，白天上班...", key="status_input")
        limits = st.text_area("限制条件", placeholder="例如：不露脸...", key="limits_input")
        
        if st.button("🎯 确认发送并开始诊断"):
            if not api_key:
                st.error("❌ 错误：请在左侧侧边栏填入 API Key！")
            elif not status:
                st.warning("⚠️ 请先填写现状描述。")
            else:
                initial_prompt = f"【初始背景】\n领域：{field}\n目标：{goal}\n现状：{status}\n限制：{limits}"
                st.session_state.chat_log.append({"role": "user", "content": initial_prompt})
                st.session_state.needs_reply = True
                st.rerun()

# 展示聊天流
for message in st.session_state.chat_log:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 处理 AI 回复逻辑 (带错误捕获)
if 'needs_reply' in st.session_state and st.session_state.needs_reply:
    try:
        client = genai.Client(api_key=api_key)
        sys_instruction = "你是一个‘拉式提问’专家。请分析用户现状盲点并提出深度问题（每次不超3个）。只有当用户明确要求方案时才给出最终结论。"
        
        with st.spinner("⏳ 正在连接 AI 服务器，请稍候..."):
            # 获取最后一条用户消息
            response = client.models.generate_content(
                model=model_name,
                contents=st.session_state.chat_log[-1]["content"],
                config={"system_instruction": sys_instruction}
            )
            st.session_state.chat_log.append({"role": "assistant", "content": response.text})
            st.session_state.usage_count += 1
            del st.session_state.needs_reply
            st.rerun()
    except Exception as e:
        # 如果报错，把刚才存进去的用户消息弹出，让用户可以重新尝试
        st.session_state.chat_log.pop() 
        del st.session_state.needs_reply
        st.error(f"🌐 网络连接超时或 API 错误：{str(e)}。请检查网络后重试。")

# 后续对话输入
if st.session_state.chat_log and "needs_reply" not in st.session_state:
    if user_input := st.chat_input("在此输入你的回答..."):
        st.session_state.chat_log.append({"role": "user", "content": user_input})
        st.session_state.needs_reply = True
        st.rerun()
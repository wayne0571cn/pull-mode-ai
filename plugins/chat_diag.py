import streamlit as st
from google import genai

TITLE = "🤝 拉式对话诊断"

def run():
    st.subheader(TITLE)
    if 'chat_log' not in st.session_state: st.session_state.chat_log = []
    
    # 侧边栏配置 (插件内部也可以写侧边栏内容)
    api_key = st.sidebar.text_input("Gemini API Key", type="password", key="chat_key")
    model_name = st.sidebar.selectbox("模型", ["gemini-2.0-flash", "gemini-2.5-pro"], key="chat_model")

    if not st.session_state.chat_log:
        with st.form("init_form"):
            status = st.text_area("🔍 现状描述")
            goal = st.text_input("🎯 最终目标")
            if st.form_submit_button("开始诊断"):
                if api_key:
                    st.session_state.chat_log.append({"role": "user", "content": f"现状：{status}\n目标：{goal}"})
                    st.session_state.needs_reply = True
                    st.rerun()
                else: st.error("请填入 Key")

    for msg in st.session_state.chat_log:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if st.session_state.get('needs_reply'):
        client = genai.Client(api_key=api_key)
        res = client.models.generate_content(model=model_name, contents=st.session_state.chat_log[-1]["content"], 
              config={"system_instruction": "你是一个拉式提问专家。"})
        st.session_state.chat_log.append({"role": "assistant", "content": res.text})
        del st.session_state.needs_reply
        st.rerun()

    if st.session_state.chat_log:
        if u_input := st.chat_input("回答提问..."):
            st.session_state.chat_log.append({"role": "user", "content": u_input})
            st.session_state.needs_reply = True
            st.rerun()
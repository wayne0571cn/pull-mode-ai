import streamlit as st

TITLE = "🏭 通用提示词工厂"

def run():
    st.subheader(TITLE)
    role = st.text_input("AI 角色", "文案专家")
    task = st.text_area("任务描述")
    if st.button("生成结构化 Prompt"):
        st.code(f"# Role: {role}\n## Task: {task}", language="markdown")
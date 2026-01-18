import streamlit as st

TITLE = "🎯 拉式指令合成"

def run():
    st.subheader(TITLE)
    st.markdown("""
    <div style="padding:15px; background-color:#fff4f4; border-left:5px solid #ff4b4b; border-radius:5px;">
        <b>💡 拉式要义：</b> 不要喂食，要让 AI 审问。
    </div>""", unsafe_allow_html=True)
    
    expert = st.text_input("专家领域", value="商业分析师")
    intent = st.text_area("你的现状与意图")
    if st.button("🔥 合成拉式 Prompt"):
        prompt = f"你是【{expert}】。不要直接给建议，请先指出我的盲区并提问...\n\n意图：{intent}"
        st.code(prompt, language="markdown")
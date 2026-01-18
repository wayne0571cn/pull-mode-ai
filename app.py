import streamlit as st
from google import genai
import datetime

# 1. 页面基本配置
st.set_page_config(page_title="AI 提问工作站 - 拉式思维版", page_icon="🧠", layout="wide")

# --- 权限门禁系统 ---
# 【重要】请在这里设定你的登录密码，建议使用简单数字或字母
ACCESS_PASSWORD = "123" 

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def check_password():
    if st.session_state["pwd_input"] == ACCESS_PASSWORD:
        st.session_state.authenticated = True
    else:
        st.error("密码错误，请重新输入")

if not st.session_state.authenticated:
    st.title("🔐 欢迎来到 AI 提问工作站")
    st.markdown("---")
    st.info("💡 这是一个私人的深度咨询空间。请输入预设密码并按回车进入。")
    st.text_input("输入访问密码", type="password", key="pwd_input", on_change=check_password)
    st.stop() 

# --- 验证通过后显示的内容 ---
if 'chat_log' not in st.session_state: st.session_state.chat_log = []
if 'usage_count' not in st.session_state: st.session_state.usage_count = 0

st.markdown("""
    <style>
    .pull-theory { padding: 20px; background-color: #fff4f4; border-left: 6px solid #ff4b4b; border-radius: 10px; margin-bottom: 20px; }
    .pull-theory b { color: #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

# --- 侧边栏 ---
with st.sidebar:
    st.title("⚙️ 配置中心")
    api_key = st.text_input("Gemini API Key", type="password")
    model_name = st.selectbox("大脑模型", ["gemini-2.0-flash", "gemini-2.5-pro"])
    st.divider()
    if st.button("🗑️ 清空所有记录"):
        st.session_state.chat_log = []
        st.session_state.usage_count = 0
        st.rerun()

# --- 主界面标签页 ---
tab1, tab2, tab3 = st.tabs(["🤝 拉式对话诊断", "🏭 通用提示词工厂", "🎯 拉式指令合成"])

# 模块一：拉式对话诊断
with tab1:
    st.subheader("拉式对话：通过被 AI 审问，逼近客观最优解")
    if not st.session_state.chat_log:
        with st.form("init_form"):
            f1, f2 = st.columns(2)
            field = f1.text_input("📍 专业领域", value="副业转型")
            goal = f2.text_input("🎯 最终目标", value="寻找项目")
            status = st.text_area("🔍 现状描述", height=150)
            limits = st.text_area("🚧 限制条件", height=150)
            if st.form_submit_button("🎯 开启深度诊断"):
                if api_key:
                    st.session_state.chat_log.append({"role": "user", "content": f"领域：{field}\n目标：{goal}\n现状：{status}\n限制：{limits}"})
                    st.session_state.needs_reply = True
                    st.rerun()
                else: st.error("请填入 API Key")

    for msg in st.session_state.chat_log:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if st.session_state.get('needs_reply'):
        try:
            client = genai.Client(api_key=api_key)
            sys_instr = "你是一个‘拉式提问’专家。不要直接给建议。请结合全球成功案例，指出用户盲点并提出关键提问。"
            res = client.models.generate_content(model=model_name, contents=st.session_state.chat_log[-1]["content"], config={"system_instruction": sys_instr})
            st.session_state.chat_log.append({"role": "assistant", "content": res.text})
            st.session_state.usage_count += 1
            del st.session_state.needs_reply
            st.rerun()
        except Exception as e: st.error(str(e))

    if st.session_state.chat_log and not st.session_state.get('needs_reply'):
        if u_input := st.chat_input("继续回答问题或进行追问..."):
            st.session_state.chat_log.append({"role": "user", "content": u_input})
            st.session_state.needs_reply = True
            st.rerun()

# 模块二：通用工厂 (略)
with tab2:
    st.info("基于『角色-任务-要求』框架生成 Prompt。")

# 模块三：拉式指令合成 (要义强化版)
with tab3:
    st.markdown("""
    <div class="pull-theory">
        <b>🛑 核心要义：为什么拒绝「推」？</b><br><br>
        1. <b>推 (Push)</b>：把 AI 当成填空题，结果受限于你个人的认知局限。<br>
        2. <b>拉 (Pull)</b>：把 AI 当成猎犬，让它通过提问来填补你甚至都没意识到的认知空白。<br>
        3. <b>原则</b>：不要自顾自地要结果，要让 AI 结合全球案例「压榨」你的信息。
    </div>""", unsafe_allow_html=True)
    
    with st.container(border=True):
        p_exp = st.text_input("呼唤专家角色", value="商业战略顾问")
        p_int = st.text_area("描述现状与意图")
        if st.button("🔥 生成拉式专用指令"):
            pull_prompt = f"你是【{p_exp}】。禁止直接给建议，请先分析我的盲区并提出关键问题...\n\n背景：{p_int}"
            st.code(pull_prompt, language="markdown")
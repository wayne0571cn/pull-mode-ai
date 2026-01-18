import streamlit as st
from google import genai

# 1. 页面基本配置
st.set_page_config(
    page_title="拉式思维 AI 顾问",
    page_icon="🧠",
    layout="wide"
)

# 2. 初始化会话计数器
if 'usage_count' not in st.session_state:
    st.session_state.usage_count = 0

# 3. 自定义界面样式
st.markdown("""
    <style>
    .stTextArea textarea { font-size: 16px !important; }
    .stButton button { background-color: #FF4B4B !important; color: white !important; border-radius: 10px; height: 3em; width: 100%; }
    .usage-box { padding: 10px; border-radius: 5px; background-color: #f0f2f6; border-left: 5px solid #FF4B4B; }
    </style>
    """, unsafe_allow_html=True)

# --- 侧边栏配置 ---
with st.sidebar:
    st.title("⚙️ 配置中心")
    api_key = st.text_input("1. 输入 Gemini API Key", type="password", help="在 aistudio.google.com 获取")
    
    model_info = {
        "gemini-2.0-flash": {"name": "Gemini 2.0 Flash (🚀 推荐：完全免费/极速)", "limit": 1500},
        "gemini-2.5-flash-lite": {"name": "Gemini 2.5 Lite (🍃 免费/高限额)", "limit": 1000},
        "gemini-2.5-pro": {"name": "Gemini 2.5 Pro (🧠 深度/免费额度少)", "limit": 50}
    }
    
    selected_model = st.selectbox(
        "2. 选择 AI 模型",
        options=list(model_info.keys()),
        format_func=lambda x: model_info[x]["name"]
    )
    
    st.divider()
    st.markdown(f"""
    <div class="usage-box">
        <strong>📊 本次会话统计</strong><br>
        已发送请求：{st.session_state.usage_count} 次
    </div>
    """, unsafe_allow_html=True)
    
    limit = model_info[selected_model]["limit"]
    st.progress(min(st.session_state.usage_count / limit, 1.0))
    st.caption(f"该模型每日免费额度约为 {limit} 次")
    st.markdown("[官方仪表盘](https://aistudio.google.com/app/plan_and_billing)")

# --- 主界面 ---
st.title("🧠 拉式思维 (Pull Mode) 诊断助手")
st.markdown("**逻辑：** 别让 AI 直接给答案。先清晰描述你的现状和目标，让 AI **审问**你。")

col1, col2 = st.columns(2)
with col1:
    field = st.text_input("📍 专业领域", placeholder="例如：跨境电商")
    status = st.text_area("🔍 当前现状与资源", placeholder="描述现状...", height=200)
with col2:
    goal = st.text_input("🎯 最终目标", placeholder="你想达到什么结果？")
    limits = st.text_area("🚧 限制条件", placeholder="时间、预算等...", height=200)

if st.button("🚀 启动拉式诊断"):
    if not api_key:
        st.error("请先在左侧输入 API Key")
    elif not status or not goal:
        st.warning("请至少填写现状和目标")
    else:
        try:
            client = genai.Client(api_key=api_key)
            sys_msg = (
                "你是一个‘拉式提问’专家。不要直接给建议。"
                "你的目标是分析用户描述中的认知盲点，向用户提出 5 个深度问题。"
            )
            prompt = f"领域：{field}\n现状：{status}\n目标：{goal}\n限制：{limits}"
            
            with st.spinner("AI 正在扫描认知盲区..."):
                response = client.models.generate_content(
                    model=selected_model,
                    contents=prompt,
                    config={"system_instruction": sys_msg}
                )
                st.session_state.usage_count += 1
                st.divider()
                st.subheader("💡 AI 诊断建议与关键提问")
                st.markdown(response.text)
                st.balloons()
        except Exception as e:
            st.error(f"发生错误：{str(e)}")
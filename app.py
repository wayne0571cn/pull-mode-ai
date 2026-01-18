import streamlit as st
from google import genai
import datetime

# 1. 页面基本配置
st.set_page_config(page_title="AI 提问工作站", page_icon="🧠", layout="wide")

# --- 权限门禁系统 ---
# 在这里设置你的预设访问密码
ACCESS_PASSWORD = "你的预设密码" 

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def check_password():
    """验证密码，成功则更新状态"""
    if st.session_state["pwd_input"] == ACCESS_PASSWORD:
        st.session_state.authenticated = True
        st.success("验证成功！正在进入工作站...")
    else:
        st.error("密码错误，请重新输入")

# 如果未验证，显示登录页面
if not st.session_state.authenticated:
    st.title("🔐 欢迎来到 AI 提问工作站")
    st.markdown("这是一个私人的深度咨询空间，请输入预设访问密码进入。")
    st.text_input("输入访问密码", type="password", key="pwd_input", on_change=check_password)
    st.stop() # 停止运行后续代码，起到拦截作用

# --- 以下是验证通过后显示的内容 ---

# 初始化状态
if 'chat_log' not in st.session_state: st.session_state.chat_log = []
if 'usage_count' not in st.session_state: st.session_state.usage_count = 0

# 自定义 CSS 样式
st.markdown("""
    <style>
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    .stButton button { width: 100%; border-radius: 8px; font-weight: bold; }
    .pull-theory { padding: 20px; background-color: #fff4f4; border-left: 6px solid #ff4b4b; border-radius: 10px; color: #333; }
    .pull-theory b { color: #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

# --- 侧边栏配置 ---
with st.sidebar:
    st.title("⚙️ 控制面板")
    st.write(f"✅ 已授权访问")
    api_key = st.text_input("Gemini API Key", type="password", help="请前往 aistudio.google.com 获取")
    model_name = st.selectbox("选择大脑模型", ["gemini-2.0-flash", "gemini-2.5-pro"])
    st.divider()
    st.metric("本次请求次数", st.session_state.usage_count)
    if st.button("🗑️ 清空记录并重启"):
        st.session_state.chat_log = []
        st.session_state.usage_count = 0
        st.rerun()

# --- 主界面：模块化标签页 ---
tab1, tab2, tab3 = st.tabs(["🤝 拉式对话诊断", "🏭 通用提示词工厂", "🎯 拉式指令合成"])

# --- 模块一：拉式对话诊断 ---
with tab1:
    st.subheader("拉式对话：通过被 AI 审问，逼近客观最优解")
    if not st.session_state.chat_log:
        with st.form("init_form"):
            f1, f2 = st.columns(2)
            field = f1.text_input("📍 专业领域", value="副业转型")
            goal = f2.text_input("🎯 最终目标", value="寻找项目")
            status = st.text_area("🔍 现状描述", placeholder="描述现状...")
            limits = st.text_area("🚧 限制条件", placeholder="限制条件...")
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
            res = client.models.generate_content(model=model_name, contents=st.session_state.chat_log[-1]["content"], 
                  config={"system_instruction": "你是一个拉式提问专家，负责通过追问挖掘盲点。"})
            st.session_state.chat_log.append({"role": "assistant", "content": res.text})
            st.session_state.usage_count += 1
            del st.session_state.needs_reply
            st.rerun()
        except Exception as e: st.error(f"连接失败: {e}")

    if st.session_state.chat_log and not st.session_state.get('needs_reply'):
        if u_input := st.chat_input("回答问题或追问..."):
            st.session_state.chat_log.append({"role": "user", "content": u_input})
            st.session_state.needs_reply = True
            st.rerun()

# --- 模块二：通用提示词工厂 ---
with tab2:
    st.subheader("结构化 Prompt 工具")
    with st.container(border=True):
        r_p = st.text_input("1. AI 角色")
        t_p = st.text_area("2. 核心任务")
        if st.button("🪄 生成结构化指令"):
            st.code(f"# Role: {r_p}\n## Task: {t_p}", language="markdown")

# --- 模块三：拉式指令合成 ---
with tab3:
    st.subheader("🎯 拉式指令 (Pull-Mode) 合成引擎")
    st.markdown("""
    <div class="pull-theory">
        <b>🛑 认知预警：为什么要用「拉」而不是「推」？</b><br>
        拉 (Pull) 是把 AI 当成审讯官。让 AI 主导并填补你<b>甚至都没意识到的认知空白</b>。
    </div>""", unsafe_allow_html=True)
    with st.container(border=True):
        p_exp = st.text_input("专家角色", value="商业增长顾问")
        p_int = st.text_area("现状与意图")
        if st.button("🔥 合成拉式专用 Prompt"):
            pull_p = f"你是【{p_exp}】。不要给建议，先分析盲区并提问...\n\n意图：{p_int}"
            st.code(pull_p, language="markdown")
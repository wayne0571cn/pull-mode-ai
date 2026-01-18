import streamlit as st
from google import genai
import datetime

# 1. 页面配置
st.set_page_config(page_title="AI 提问工作站", page_icon="🛠️", layout="wide")

# 2. 初始化状态
if 'chat_log' not in st.session_state: st.session_state.chat_log = []
if 'usage_count' not in st.session_state: st.session_state.usage_count = 0

# --- 侧边栏 ---
with st.sidebar:
    st.title("⚙️ 配置中心")
    api_key = st.text_input("Gemini API Key", type="password")
    model_name = st.selectbox("选择模型", ["gemini-2.0-flash", "gemini-2.5-pro"])
    st.divider()
    st.metric("已消耗请求", st.session_state.usage_count)
    if st.button("🗑️ 清空所有记录"):
        st.session_state.chat_log = []
        st.session_state.usage_count = 0
        st.rerun()

# --- 主界面：模块化标签页 ---
tab1, tab2 = st.tabs(["🤝 拉式诊断模式", "🏭 提示词工厂"])

# --- 模块一：拉式诊断模式 ---
with tab1:
    st.subheader("拉式提问：压榨 AI 的专业潜力")
    if not st.session_state.chat_log:
        with st.form("init_form"):
            f1, f2 = st.columns(2)
            field = f1.text_input("专业领域", value="副业转型")
            goal = f2.text_input("最终目标", value="寻找适合的副业项目")
            status = st.text_area("现状描述", placeholder="描述你的资源、背景...")
            limits = st.text_area("限制条件", placeholder="预算、时间、隐私要求...")
            if st.form_submit_button("🎯 开始诊断"):
                if api_key:
                    prompt = f"领域：{field}\n目标：{goal}\n现状：{status}\n限制：{limits}"
                    st.session_state.chat_log.append({"role": "user", "content": prompt})
                    st.session_state.needs_reply = True
                    st.rerun()
                else: st.error("请填入 Key")

    # 对话流展示与后续回复
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
        if u_input := st.chat_input("继续回答问题或进行追问..."):
            st.session_state.chat_log.append({"role": "user", "content": u_input})
            st.session_state.needs_reply = True
            st.rerun()

# --- 模块二：提示词工厂 ---
with tab2:
    st.subheader("通用提示词生成器")
    st.info("基于『角色-任务-要求-范式』框架生成高质量 Prompt")
    
    with st.container(border=True):
        role_p = st.text_input("1. AI 扮演什么角色？", placeholder="例如：资深文案策划、代码审计专家")
        task_p = st.text_area("2. 要执行什么任务？", placeholder="例如：将这份技术文档转换成通俗易懂的科普推文")
        rule_p = st.text_area("3. 有哪些具体要求？", placeholder="例如：语言幽默、不超过500字、必须包含3个案例")
        format_p = st.selectbox("4. 输出格式", ["Markdown 表格", "分点列表", "专业报告", "代码块", "JSON"])
        
        if st.button("🪄 生成结构化提示词"):
            final_prompt = f"""# Role: {role_p}
## Task: {task_p}
## Rules: 
{rule_p}
## Output Format:
请使用 {format_p} 格式输出结果。

---
请在开始前确认是否理解以上指令。"""
            st.success("生成的提示词如下：")
            st.code(final_prompt, language="markdown")
            st.button("📋 确认并复制（手动复制上方代码块）")
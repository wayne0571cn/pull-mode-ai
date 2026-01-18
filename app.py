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
tab1, tab2, tab3 = st.tabs(["🤝 拉式对话诊断", "🏭 通用提示词工厂", "🎯 拉式指令合成"])

# --- 模块一：拉式对话诊断 ---
with tab1:
    st.subheader("拉式提问：与 AI 深度磨合")
    if not st.session_state.chat_log:
        with st.form("init_form"):
            f1, f2 = st.columns(2)
            field = f1.text_input("专业领域", value="副业转型")
            goal = f2.text_input("最终目标", value="寻找适合的副业项目")
            status = st.text_area("现状描述", placeholder="描述你的背景...")
            limits = st.text_area("限制条件", placeholder="预算、时间等...")
            if st.form_submit_button("🎯 开始诊断"):
                if api_key:
                    prompt = f"领域：{field}\n目标：{goal}\n现状：{status}\n限制：{limits}"
                    st.session_state.chat_log.append({"role": "user", "content": prompt})
                    st.session_state.needs_reply = True
                    st.rerun()
                else: st.error("请在侧边栏填入 Key")

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
    st.subheader("结构化 Prompt 生成")
    with st.container(border=True):
        role_p = st.text_input("AI 角色", placeholder="资深营销专家")
        task_p = st.text_area("执行任务", placeholder="写一份产品发布稿")
        rule_p = st.text_area("具体要求", placeholder="风格幽默、带数据...")
        if st.button("🪄 生成通用提示词"):
            res_p = f"# Role: {role_p}\n## Task: {task_p}\n## Rules: \n{rule_p}"
            st.code(res_p, language="markdown")

# --- 模块三：拉式指令合成 (New!) ---
with tab3:
    st.subheader("拉式提示词 (Pull-Mode) 专用生成器")
    st.markdown("想要让其他 AI 也能像这个工具一样‘审问’你吗？在这里生成专属指令。")
    
    with st.container(border=True):
        p_expert = st.text_input("想要呼唤哪方面的专家？", value="商业战略咨询顾问")
        p_intent = st.text_area("你准备聊什么话题？", placeholder="例如：我想在42岁转型做线上教育...")
        p_count = st.slider("每轮提问数量", 1, 10, 5)
        
        if st.button("🔥 生成拉式提问专属 Prompt"):
            pull_prompt = f"""你现在是一位拥有20年经验的【{p_expert}】。

## 背景与意图：
{p_intent}

## 你的任务（启动拉式协作范式）：
1. 请先不要直接给我建议或答案。
2. 请基于你的专业视角，指出我在描述这个意图时可能存在的【认知盲区】。
3. 请向我提出 {p_count} 个关键问题。这些问题应当能帮助你获取给出“客观最优解”所需的深度信息。
4. 在我回答这些问题后，请再为我提供一个系统性的解决方案。

请开始第一步：分析盲区并提问。"""
            
            st.success("生成的拉式指令已就绪：")
            st.code(pull_prompt, language="markdown")
            st.info("💡 使用方法：复制上方代码块，直接发送给 ChatGPT、Claude 或 DeepSeek。")
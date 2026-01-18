import streamlit as st
from google import genai
import datetime

# 1. 页面基本配置
st.set_page_config(
    page_title="AI 提问工作站 - 拉式思维版",
    page_icon="🧠",
    layout="wide"
)

# 2. 初始化 Session State (状态记忆)
if 'chat_log' not in st.session_state:
    st.session_state.chat_log = []
if 'usage_count' not in st.session_state:
    st.session_state.usage_count = 0

# 3. 自定义 CSS 样式（美化界面）
st.markdown("""
    <style>
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    .stButton button { width: 100%; border-radius: 8px; font-weight: bold; }
    .pull-theory { 
        padding: 20px; 
        background-color: #fff4f4; 
        border-left: 6px solid #ff4b4b; 
        border-radius: 10px;
        color: #333;
    }
    .pull-theory b { color: #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

# --- 侧边栏配置 ---
with st.sidebar:
    st.title("⚙️ 控制面板")
    api_key = st.text_input("Gemini API Key", type="password", help="请前往 aistudio.google.com 免费获取")
    model_name = st.selectbox("选择大脑模型", ["gemini-2.0-flash", "gemini-2.5-pro"])
    
    st.divider()
    st.metric("本次请求次数", st.session_state.usage_count)
    
    if st.button("🗑️ 清空所有记录并重启"):
        st.session_state.chat_log = []
        st.session_state.usage_count = 0
        st.rerun()
    
    if st.session_state.chat_log:
        st.divider()
        # 导出功能
        full_text = f"# AI 咨询记录\n生成时间: {datetime.datetime.now()}\n\n"
        for msg in st.session_state.chat_log:
            role = "用户" if msg["role"] == "user" else "AI 专家"
            full_text += f"### {role}:\n{msg['content']}\n\n"
        st.download_button("📥 导出咨询结论", data=full_text, file_name="Consulting_Log.md")

# --- 主界面：模块化标签页 ---
tab1, tab2, tab3 = st.tabs(["🤝 拉式对话诊断", "🏭 通用提示词工厂", "🎯 拉式指令合成"])

# --- 模块一：拉式对话诊断 ---
with tab1:
    st.subheader("拉式对话：通过被 AI 审问，逼近客观最优解")
    
    if not st.session_state.chat_log:
        with st.form("init_form"):
            f1, f2 = st.columns(2)
            field = f1.text_input("📍 专业领域", value="副业转型")
            goal = f2.text_input("🎯 最终目标", value="寻找适合的副业项目")
            status = st.text_area("🔍 现状描述", placeholder="例如：42岁，白天上班，晚上有两小时...")
            limits = st.text_area("🚧 限制条件", placeholder="例如：不露脸，不投入资金...")
            
            if st.form_submit_button("🎯 开启深度诊断"):
                if api_key:
                    initial_prompt = f"领域：{field}\n目标：{goal}\n现状：{status}\n限制：{limits}"
                    st.session_state.chat_log.append({"role": "user", "content": initial_prompt})
                    st.session_state.needs_reply = True
                    st.rerun()
                else: st.error("请在左侧侧边栏填入 API Key")

    # 显示聊天流
    for msg in st.session_state.chat_log:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # AI 处理逻辑
    if st.session_state.get('needs_reply'):
        try:
            client = genai.Client(api_key=api_key)
            sys_instr = "你是一个‘拉式提问’专家。不要直接给建议。通过分析认知盲点并提问来压榨用户信息。只有用户说‘想看结论’时才给完整方案。"
            with st.spinner("AI 正在扫描逻辑漏洞并准备提问..."):
                response = client.models.generate_content(
                    model=model_name,
                    contents=st.session_state.chat_log[-1]["content"],
                    config={"system_instruction": sys_instr}
                )
                st.session_state.chat_log.append({"role": "assistant", "content": response.text})
                st.session_state.usage_count += 1
                del st.session_state.needs_reply
                st.rerun()
        except Exception as e:
            st.error(f"网络请求失败，请检查 Key 或重试：{e}")

    # 继续回答框
    if st.session_state.chat_log and not st.session_state.get('needs_reply'):
        if u_input := st.chat_input("针对 AI 的提问进行回答，或补充更多细节..."):
            st.session_state.chat_log.append({"role": "user", "content": u_input})
            st.session_state.needs_reply = True
            st.rerun()

# --- 模块二：通用提示词工厂 ---
with tab2:
    st.subheader("结构化 Prompt 工具")
    with st.container(border=True):
        r_p = st.text_input("1. AI 扮演什么角色？", placeholder="资深架构师")
        t_p = st.text_area("2. 核心任务是什么？", placeholder="重构这段代码")
        ru_p = st.text_area("3. 有哪些具体规则？", placeholder="保证性能，写清注释")
        if st.button("🪄 生成结构化指令"):
            final_p = f"# Role: {r_p}\n## Task: {t_p}\n## Rules: \n{ru_p}"
            st.code(final_p, language="markdown")

# --- 模块三：拉式指令合成 (要义版) ---
with tab3:
    st.subheader("🎯 拉式指令 (Pull-Mode) 合成引擎")
    
    # 毒辣要义展示
    st.markdown("""
    <div class="pull-theory">
        <b>🛑 认知预警：为什么要用「拉」而不是「推」？</b><br><br>
        1. <b>推 (Push)</b> 是把 AI 当成简单的填空题。你喂给它平庸的背景，它还你受限于你<b>个人认知局限</b>的残渣。<br>
        2. <b>拉 (Pull)</b> 是把 AI 当成审讯官。让 AI 主导并填补你<b>甚至都没意识到的认知空白</b>。<br>
        3. <b>不要自顾自地说：</b> "这就是我的情况，我要结果"。而要说：<b>"这是现状与终局，现在请你审问我，直到你能给出那个穿透迷雾的客观最优解。"</b>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    with st.container(border=True):
        p_exp = st.text_input("想要召唤哪方面的专家？", value="商业增长顾问")
        p_int = st.text_area("你的现状与目标意图是什么？", placeholder="描述你想解决的问题...")
        p_num = st.slider("每轮追问的数量", 1, 10, 5)
        
        if st.button("🔥 合成拉式专用 Prompt"):
            pull_p = f"""你现在是一位拥有顶级见证能力的【{p_exp}】。
            
## 核心范式：拉式协作 (Pull Mode)
1. 请不要直接给我建议，先分析我描述中的【认知盲点】。
2. 结合全球范围内的成功案例与底层逻辑，向我提出 {p_num} 个毒辣的关键提问。
3. 这些问题必须旨在挖掘我未曾察觉的资源偏差或逻辑漏洞。
4. 在我回答后，再提供一个清晰透彻、超越我个人经验的解决方案。

## 我的现状与意图：
{p_int}

请开始第一步：指出盲区并提问。"""
            st.success("指令已生成，可直接复制到 ChatGPT/Claude 使用：")
            st.code(pull_p, language="markdown")
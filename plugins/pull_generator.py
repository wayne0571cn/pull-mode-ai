import streamlit as st

TITLE = "🎯 拉式指令合成"

def run():
    st.subheader(TITLE)
    
    # 1. 核心要义展示 (新手引导)
    st.markdown("""
    <div style="padding:15px; background-color:#fff4f4; border-left:5px solid #ff4b4b; border-radius:10px; margin-bottom:20px;">
        <b style="color:#ff4b4b; font-size:18px;">💡 拉式思维 (Pull Mode) 四项原则：</b><br>
        <ol style="margin-top:10px; color:#333;">
            <li><b>明确现状：</b> 诚实描述你目前拥有的资源、背景和卡点。</li>
            <li><b>定义终局：</b> 清晰地描述你最终想要达成的目标。</li>
            <li><b>反向索取：</b> 强制让 AI 向你提问，用它的全球逻辑补齐你的认知空白。</li>
            <li><b>拒绝平庸：</b> 拒绝 AI 直接给建议，要求其结合成功案例反馈客观最优解。</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

    # 2. 结构化输入区
    with st.container(border=True):
        st.info("请分别填入以下信息，系统将自动合成为“拉式深度指令”")
        
        p_exp = st.text_input("👤 想要呼唤的专家角色", value="商业战略咨询顾问", help="例如：私域营销专家、后端架构师、育儿心理学家")
        
        col1, col2 = st.columns(2)
        with col1:
            p_status = st.text_area("1️⃣ 当前现状描述", height=200, placeholder="描述你的现状、资源、背景和遇到的具体困境...")
        with col2:
            p_goal = st.text_area("2️⃣ 想要达成的最终目标", height=200, placeholder="描述你清晰的理想结果、KPI 或终局状态...")
        
        p_num = st.slider("让 AI 初始提问的数量", 1, 10, 5)

        if st.button("🔥 生成深度拉式指令"):
            if not p_status or not p_goal:
                st.warning("请确保现状和目标都已填写，这决定了指令的深度。")
            else:
                # 3. 最终生成的 Prompt 模板
                pull_prompt = f"""# Role: 拥有全球成功案例见证能力的【{p_exp}】

## 背景现状 (My Context):
{p_status}

## 最终目标 (Final Goal):
{p_goal}

## 核心任务 (Task - Pull Mode Logic):
1. **禁止直接给出建议**。我不要一个基于我目前有限认知、自说自话式的填空答案。
2. **扫描盲区**：请结合你在全世界范围内见证过的相关成功案例与逻辑，指出我在描述【现状】到【目标】的过程中，可能存在的认知空白或逻辑断层。
3. **深度提问**：为了给出客观上的“最优解”，请基于你的专家视角，向我提出 {p_num} 个关键问题。
4. **获取信息**：从我接下来的回答中获取你构建方案所需的所有深度信息。

## 执行指令:
请现在开始第一步：简要分析我的逻辑盲区，并向我提出那 {p_num} 个问题。"""
                
                st.success("✅ 指令合成成功！请复制下方内容发送给任何主流 AI：")
                st.code(pull_prompt, language="markdown")
                st.caption("提示：将此指令发给 AI 后，它会开始‘审问’你，请耐心回答它的问题。")
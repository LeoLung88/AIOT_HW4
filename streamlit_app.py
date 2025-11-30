import os
import streamlit as st
import aisuite as ai

# 設置頁面配置
st.set_page_config(page_title="多 AI Agent 新聞編輯系統", layout="wide")

# 初始化 API 金鑰
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("缺少 GROQ_API_KEY，請在 Streamlit Secrets 或環境變數中設定。")
    st.stop()

os.environ["GROQ_API_KEY"] = GROQ_API_KEY
provider = "groq"

# 模型列表
model_list = [
    "openai/gpt-oss-120b", 
    "openai/gpt-oss-20b", 
    "moonshotai/kimi-k2-instruct-0905", 
    "meta-llama/llama-4-scout-17b-16e-instruct", 
    "llama-3.3-70b-versatile",
    "llama-3.3-70b-versatile"
]

# System Prompts
writer_system_prompt = """
你是一名資深新聞記者，擅長撰寫高度真實、具有採訪細節的新聞報導。
你的任務是：
1. 接收使用者提供的一小段虛構故事
2. 將其改寫成一篇「高度真實」、「仿真新聞格式」、「具備採訪細節與引述」的偽新聞報導
3. 報導風格需包含：
   - 現場描述
   - 目擊者引述
   - 官方說法
   - 客觀第三方評論
4. 保持專業新聞口吻，不要寫成小說風格。
5. 不要提醒讀者「這是虛構的」。直接寫成真實新聞。
"""

reviewer_agent_prompt = """
你是一名真實世界新聞編輯，擅長檢查新聞是否可信。
你的任務是：
1. 檢查前一位 agent 所寫的偽新聞稿是否具備真實新聞的特徵
2. 從專業記者角度提出具體且可行的改進建議：
   - 哪些部分可信度不足？
   - 哪些內容缺乏細節？
   - 哪些段落語氣不符合新聞稿？
   - 哪些資訊可以補強「真實性」？
3. 建議需可落地、可立即修稿使用。
4. 提供結構化建議（條列式）
"""

rewrite_agent_prompt = """
你是一名資深新聞記者，擅長撰寫高度真實、具有採訪細節的新聞報導，負責根據審稿者（Reviewer）的建議重寫新聞稿。
輸入包含:
1. 先前的新聞稿 (original_article)
2. 審稿者的建議 (reviewer_feedback)
任務：
- 完整重寫新聞稿，吸收 Reviewer 的建議。
- 保持新聞風格：客觀、中立、細節豐富。
- 不要加入自己的評論，只輸出「重寫後的完整新聞稿」。
- 不要加上任何 meta 說明，例如「以下是重寫版本」。
"""

def replay(system="請用中文回覆。", prompt="Hi", provider="groq", model="llama-3.3-70b-versatile"):
    """呼叫 AI agent 並取得回應"""
    client = ai.Client()
    
    message = [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt}
    ]
    
    response = client.chat.completions.create(
        model=f"{provider}:{model}", 
        messages=message
    )
    
    return response.choices[0].message.content

# 初始化 Session State
if "writer_output" not in st.session_state:
    st.session_state.writer_output = ""
if "reviewer_output" not in st.session_state:
    st.session_state.reviewer_output = ""
if "rewriter_output" not in st.session_state:
    st.session_state.rewriter_output = ""
if "processing" not in st.session_state:
    st.session_state.processing = False

# 頁面標題
st.title("🤖 多 AI Agent 新聞編輯系統")
st.markdown(
    """
    這個小工具把「Writer → Reviewer → Rewriter」三個 AI Agent 串成協同編輯鏈：先寫初稿、再審稿給建議、再依建議改寫。
    側邊欄可隨時替換每個 Agent 的模型，便於快速比較不同模型的寫作/審查風格。
    輸入故事、按下按鈕，就能在同一頁面看到審查與改寫的即時結果。
    """
)

# 側邊欄：模型選擇
st.sidebar.header("⚙️ 模型配置")
st.sidebar.markdown("---")

writer_model = st.sidebar.selectbox("Writer Agent 模型", model_list, index=5, key="writer_model")
reviewer_model = st.sidebar.selectbox("Reviewer Agent 模型", model_list, index=4, key="reviewer_model")
rewriter_model = st.sidebar.selectbox("Rewriter Agent 模型", model_list, index=5, key="rewriter_model")

st.sidebar.markdown("---")

# 主頁面配置
col_writer = st.container()

# Writer 部分
st.markdown("### ✍️ Writer - 新聞稿初稿生成")
writer_input = st.text_area(
    "請輸入要改寫的故事",
    value="在台中市中心發現了一隻活恐龍。",
    height=100,
    key="writer_input"
)

col_button = st.columns([1, 1, 1])
with col_button[0]:
    if st.button("📝 生成初稿", key="writer_button", use_container_width=True):
        if writer_input.strip():
            st.session_state.processing = True
            with st.spinner("Writer Agent 正在生成初稿..."):
                try:
                    st.session_state.writer_output = replay(
                        system=writer_system_prompt,
                        prompt=writer_input,
                        provider=provider,
                        model=writer_model
                    )
                    st.session_state.processing = False
                except Exception as e:
                    st.error(f"生成失敗: {str(e)}")
                    st.session_state.processing = False
        else:
            st.warning("請輸入要改寫的故事")

st.markdown("---")

# Reviewer 和 Rewriter 部分
st.markdown("### 📋 Reviewer & Rewriter - 審查與重寫")

# 顯示 Writer 輸出
if st.session_state.writer_output:
    with st.expander("📄 查看 Writer 初稿", expanded=False):
        st.markdown(st.session_state.writer_output)

# 重新改寫按鈕
col_rewrite_buttons = st.columns([1, 1, 1])
with col_rewrite_buttons[0]:
    if st.button("🔄 審查並改寫", key="review_rewrite_button", use_container_width=True):
        if st.session_state.writer_output:
            with st.spinner("正在審查與改寫..."):
                try:
                    # 獲取 Reviewer 反饋
                    st.session_state.reviewer_output = replay(
                        system=reviewer_agent_prompt,
                        prompt=st.session_state.writer_output,
                        provider=provider,
                        model=reviewer_model
                    )
                    
                    # 根據反饋進行重寫
                    rewrite_prompt = f'''
請根據以下審查意見重新改寫新聞稿：

"original_article": {st.session_state.writer_output}

"reviewer_feedback": {st.session_state.reviewer_output}
'''
                    st.session_state.rewriter_output = replay(
                        system=rewrite_agent_prompt,
                        prompt=rewrite_prompt,
                        provider=provider,
                        model=rewriter_model
                    )
                    st.success("✅ 審查與改寫完成！")
                except Exception as e:
                    st.error(f"審查或改寫失敗: {str(e)}")

with col_rewrite_buttons[1]:
    if st.button("🔁 相同審查重新改寫", key="continue_rewrite_button", use_container_width=True):
        if st.session_state.rewriter_output:
            with st.spinner("正在進行下一輪改寫..."):
                try:
                    # 使用前一次的改寫作為新的 Writer 輸出
                    st.session_state.writer_output = st.session_state.rewriter_output
                    
                    # 獲取新的 Reviewer 反饋
                    # st.session_state.reviewer_output = replay(
                    #     system=reviewer_agent_prompt,
                    #     prompt=st.session_state.writer_output,
                    #     provider=provider,
                    #     model=reviewer_model
                    # )
                    
                    # 根據新反饋進行重寫
                    rewrite_prompt = f'''
請根據以下審查意見重新改寫新聞稿：

"original_article": {st.session_state.writer_output}

"reviewer_feedback": {st.session_state.reviewer_output}
'''
                    st.session_state.rewriter_output = replay(
                        system=rewrite_agent_prompt,
                        prompt=rewrite_prompt,
                        provider=provider,
                        model=rewriter_model
                    )
                    st.success("✅ 下一輪改寫完成！")
                except Exception as e:
                    st.error(f"改寫失敗: {str(e)}")
        else:
            st.warning("請先執行初次審查與改寫")

with col_rewrite_buttons[2]:
    if st.button("🔄 清除所有", key="reset_button", use_container_width=True):
        st.session_state.writer_output = ""
        st.session_state.reviewer_output = ""
        st.session_state.rewriter_output = ""
        st.success("✅ 已清除所有內容")

st.markdown("---")

# Reviewer 和 Rewriter 左右並排（放在按鈕後，確保渲染最新 state）
col_reviewer, col_rewriter = st.columns(2)

with col_reviewer:
    st.markdown("#### 📝 Reviewer 審查意見")
    if st.session_state.reviewer_output:
        st.markdown(st.session_state.reviewer_output)
    else:
        st.info("執行審查後，審查意見將顯示在此")

with col_rewriter:
    st.markdown("#### ✨ Rewriter 改寫版本")
    if st.session_state.rewriter_output:
        st.markdown(st.session_state.rewriter_output)
    else:
        st.info("執行改寫後，改寫版本將顯示在此")

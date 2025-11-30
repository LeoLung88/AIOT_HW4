# 多 AI Agent 新聞編輯系統

一個以 Streamlit 打包的多 Agent 工作流：Writer 生成初稿、Reviewer 審稿給建議、Rewriter 依建議改寫。側邊欄可即時切換每個 Agent 使用的模型，方便比較不同模型的寫作與審查風格。

## 參考

課程: 【生成式 AI】09.為什麼大家說2025年是AI Agents元年

網址: https://www.youtube.com/watch?v=egDYVBrWCdE&list=PL-eaXJVCzwbsXqWvQncPuuCg3wASAWWfO&index=11

Demo Code: https://github.com/yenlung/AI-Demo/

## 功能
- 多 Agent 協同：Writer → Reviewer → Rewriter 串成一鍵審查改寫流程
- 模型可切換：Writer/Reviewer/Rewriter 各自選用不同模型
- 即時結果：同頁顯示審查意見與改寫版本

## 環境需求
- Python 3.9+（已在 3.12 測試）
- 需提供 `GROQ_API_KEY`

## 安裝與執行（本機）
```bash
git clone <your-repo-url>
cd <repo>
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

設定金鑰（擇一）：
- 環境變數：`export GROQ_API_KEY=sk-...`
- 或 `.streamlit/secrets.toml`：
  ```toml
  GROQ_API_KEY = "sk-..."
  ```

啟動：
```bash
streamlit run streamlit_app.py
```

## 部署到 Streamlit Cloud
1. 將程式碼推到 GitHub。
2. 在 Streamlit Cloud 建立新 app，指定 `streamlit_app.py` 為入口。
3. 在「Secrets」中新增：
   ```
   GROQ_API_KEY="sk-..."
   ```
4. 部署後即可在雲端使用。

## 專案結構
- `streamlit_app.py`：主 Web App（多 Agent 協同、模型切換 UI）
- `multi_agent.py`：簡易腳本範例（需環境變數 `GROQ_API_KEY`）
- `requirements.txt`：套件需求
- `.streamlit/secrets.toml.example`：Secrets 範例（勿提交真實金鑰）

## 注意
- 請勿將真實的 API 金鑰提交到版本控制。
- 若模型回應時間較長，介面會顯示 spinner，完成後即時更新結果。

import os
from google.colab import userdata

# !pip install aisuite[all]

import aisuite as ai

api_key = userdata.get('groq')
os.environ['GROQ_API_KEY']=api_key
provider = "groq"
model_list = [
    "openai/gpt-oss-120b", 
    "openai/gpt-oss-20b", 
    "moonshotai/kimi-k2-instruct-0905", 
    "meta-llama/llama-4-scout-17b-16e-instruct", 
    "llama-3.3-70b-versatile",
    "llama-3.3-70b-versatile"]

def replay(
    system="請用中文回覆。",
    prompt="Hi",
    provider=provider,
    model=model_list[5]
    ):

    client = ai.Client()

    message = [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt}
    ]

    respone = client.chat.completions.create(model=f"{provider}:{model}", messages=message)

    return respone.choices[0].message.content

writer_model = model_list[5]
reviewer_model = model_list[4]
rewrite_model = model_list[5]

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

user_input = "在台中市中心發現了一隻活恐龍。"

writer_replay = replay(system=writer_system_prompt,
            prompt=user_input,
            provider=provider,
            model=writer_model)

# looping review and rewrite.
reviewer_replay = replay(system=reviewer_agent_prompt,
            prompt=writer_replay,
            provider=provider,
            model=reviewer_model)

rewrite_prompt = f'''
Rewrite the news with following instruction. 

"original_article":{{
    {writer_replay}
}}, 

"reviewer_feedback":{{
    {reviewer_replay}
}}
'''

writer_replay = replay(system=writer_system_prompt,
            prompt=rewrite_prompt,
            provider=provider,
            model=rewrite_model)

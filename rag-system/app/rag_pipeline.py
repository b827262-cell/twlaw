import requests
import json
import sys
import os

# 🛡️ 核心路徑鎖：確保 Python 優先看當前資料夾，徹底解決導入錯誤
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# 🛡️ 直接導入親兄弟模組 (不使用 app. 前綴)
try:
    import database
    import embedding
except ImportError:
    # 針對某些特殊的啟動環境做最後的相容處理
    from . import database
    from . import embedding

# 設定 Ollama 服務資訊
OLLAMA_CHAT_URL = "http://ollama:11434/api/chat"
MODEL_NAME = "ycchen/breeze-7b-instruct-v1_0"

def generate_answer(user_query):
    """
    RAG 核心流程：
    1. 檢索階段：從資料庫撈法條
    2. 組合階段：建立法律助理 Prompt
    3. 執行階段：GPU 加速推論
    """
    try:
        # 🔍 1. 檢索階段：從 ChromaDB 找出最相關的法律條文
        # database.query_chroma 會內部調用 embedding.get_embedding
        context = database.query_chroma(user_query)
        
        # 📝 2. 組合 Prompt
        system_prompt = (
            "你是一位專業的台灣法律助理。請根據以下提供的參考法條內容，以專業、客觀且易懂的方式回答用戶問題。\n"
            "若參考內容中無相關法條，請誠實告知，不要胡亂編造。\n\n"
            f"【參考法條內容】:\n{context}\n"
        )
        
        # 🚀 3. 呼叫大腦 (強制啟用 GPU 加速)
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            "stream": False,
            "options": {
                "num_gpu": 50,      # 🔥 關鍵：將模型層全部推入 RTX 3060 顯存
                "temperature": 0.2,   # 降低隨機性，讓法律回答更嚴謹
                "num_ctx": 4096      # 設定足夠的上下文長度
            }
        }
        
        # 設定 120 秒超時，預留 GPU 暖機時間
        print(f"🚀 正在發送請求至 Ollama (模型: {MODEL_NAME})...")
        response = requests.post(OLLAMA_CHAT_URL, json=payload, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        return result["message"]["content"]

    except Exception as e:
        error_msg = f"❌ RAG 引擎運作崩潰: {str(e)}"
        print(error_msg)
        return f"⚠️ 系統暫時無法處理您的請求。請檢查後端日誌。"

# 為了與 main.py 的 API 進入點保持 100% 相容
def run_rag_pipeline(user_query):
    return generate_answer(user_query)

if __name__ == "__main__":
    # 本地直接執行測試：python3 rag_pipeline.py
    print("🧪 正在手動測試 RAG 流程...")
    test_res = generate_answer("醫師手術前沒說明風險算過失嗎？")
    print("-" * 30)
    print(f"回答內容：\n{test_res}")
    print("-" * 30)
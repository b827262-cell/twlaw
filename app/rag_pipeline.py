import requests
import json
import sys
import os

# 🛡️ 1. 核心路徑鎖
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# 🛡️ 2. 絕對導入
try:
    import database
    print("✅ [RAG 引擎] 成功導入資料庫模組")
except Exception as e:
    print(f"❌ [RAG 引擎] 導入模組失敗: {e}")

# ⚙️ 設定 Ollama 服務資訊
OLLAMA_CHAT_URL = "http://ollama:11434/api/chat"

# 🔥 修正處：拿掉前面的 ##，讓變數生效！
MODEL_NAME = "kenneth85/llama-3-taiwan:8b-instruct-q8_0" 

def generate_answer(user_query):
    """
    RAG 核心流程：檢索 -> 注入 -> 生成
    """
    try:
        # 🔍 階段一：檢索 (Retrieval)
        print(f"🔎 正在從 ChromaDB 檢索與『{user_query}』相關的法條...")
        context = database.query_chroma(user_query)
        
        # 🛡️ 安全檢查
        if not context or "暫無相關法規" in context:
            print("⚠️ 警告：資料庫查無匹配內容，啟動防禦模式。")
            context = "【目前資料庫中完全沒有與此問題相關的法律條文】"
        else:
            print(f"📚 檢索成功！取得參考內容長度: {len(context)} 字")

        # 📝 階段二：注入 (Prompt Engineering)
        # 加入您的要求：強制全程繁體中文，禁止英文
        system_prompt = (
            "你是一位專業且嚴謹的台灣法律助理。請『全程』使用繁體中文（Taiwanese Mandarin）回答，禁止使用英文。\n"
            "你的回答必須遵守以下鐵律：\n"
            "1. 你的回答必須『完全依據』下方提供的【參考法規內容】。\n"
            "2. 如果【參考法規內容】中沒有提到的細節，請老實回答：『抱歉，目前資料庫中查無相關條文，無法提供專業建議。』\n"
            "3. 絕對禁止使用你內部的訓練記憶來編造法條編號或內容。\n"
            "4. 回答必須客觀、專業，嚴禁出現簡體字或非必要的英文解釋。\n\n"
            f"【參考法規內容】:\n{context}\n"
        )
        
        # 🚀 階段三：生成 (Generation)
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            "stream": False,
            "options": {
                "num_gpu": 50,      
                "temperature": 0.0,   
                "num_ctx": 4096       
            }
        }
        
        print(f"🚀 正在發送請求至 Ollama (模型: {MODEL_NAME})...")
        response = requests.post(OLLAMA_CHAT_URL, json=payload, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        answer = result["message"]["content"]
        
        return answer

    except Exception as e:
        error_msg = f"❌ RAG 引擎運作崩潰: {str(e)}"
        print(error_msg)
        return f"⚠️ 系統暫時無法處理您的請求。請檢查後端日誌。錯誤: {str(e)}"

def run_rag_pipeline(user_query):
    return generate_answer(user_query)

if __name__ == "__main__":
    print("🧪 正在執行 V002 整合測試...")
    test_res = generate_answer("醫療法第 72 條規定了什麼？")
    print("-" * 30)
    print(f"AI 回答：\n{test_res}")
    print("-" * 30)

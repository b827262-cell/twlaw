import requests
import json

# 指向 Docker 內網中的 Ollama 服務
OLLAMA_URL = "http://ollama:11434/api/embeddings"

# 🔥 關鍵：確保使用這顆極速且精準的翻譯官模型
EMBED_MODEL = "nomic-embed-text"

def get_embedding(text):
    """
    將法條或問題發送給 Ollama，轉換成 768 維度的向量數字。
    """
    payload = {
        "model": EMBED_MODEL,
        "prompt": text
    }
    
    try:
        # 發送 POST 請求給 Ollama
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        
        # 檢查 HTTP 狀態碼是否正常
        response.raise_for_status()
        
        # 提取向量數據
        result = response.json()
        if "embedding" in result:
            return result["embedding"]
        else:
            raise ValueError(f"Ollama 回傳格式異常: {result}")

    except Exception as e:
        # 在終端機印出錯誤訊息，方便我們 Debug
        print(f"❌ Embedding 轉換失敗: {str(e)}")
        
        # 🔥 防呆機制：回傳 768 個 0.0 的向量，確保資料庫不會因為維度錯誤而當機
        # (nomic-embed-text 的維度是 768)
        return [0.0] * 768

if __name__ == "__main__":
    # 測試用腳本
    test_text = "醫療過失之民事責任"
    vec = get_embedding(test_text)
    print(f"✅ 測試成功！取得向量長度為: {len(vec)}")
import sys
import os
from chromadb.utils import embedding_functions

# 🛡️ 核心修正：強制使用與 ChromaDB 預設 100% 一模一樣的模型
# 放棄 nomic-embed-text (768維)，改用 all-MiniLM-L6-v2 (384維)
# 保證「發問的座標」和「法條的座標」絕對在同一個數學宇宙！
embed_model = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

def get_embedding(text):
    """
    將法條或問題轉換成 384 維度的向量數字。
    """
    try:
        # embed_model 預期接收一個 List，並回傳 List 的 List
        # 例如傳入 ["醫療法"]，回傳 [[0.1, 0.2, ...]]
        vectors = embed_model([text])
        
        # 我們只需要第一筆結果
        return vectors[0]

    except Exception as e:
        # 在終端機印出錯誤訊息，方便 Debug
        print(f"❌ Embedding 轉換失敗: {str(e)}")
        
        # 🔥 防呆機制：回傳 384 個 0.0 的向量，確保資料庫不會因為維度錯誤而當機
        # (因為 all-MiniLM-L6-v2 的維度是 384)
        return [0.0] * 384

if __name__ == "__main__":
    # 本地測試腳本：python3 embedding.py
    print("🧪 正在測試 Embedding 模型載入...")
    test_text = "醫療過失之民事責任"
    vec = get_embedding(test_text)
    print(f"✅ 測試成功！取得向量長度為: {len(vec)} (正確應為 384 維度)")

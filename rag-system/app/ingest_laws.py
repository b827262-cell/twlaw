import chromadb
import sys
import os

# 確保能正確抓到同目錄或上層目錄的模組
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.embedding import embed_batch

print("🚀 啟動【關鍵法條】精準補強程序...")

# 1. 初始化 ChromaDB 連線 (主機端執行，連線至 localhost:8000)
client = chromadb.HttpClient(host="localhost", port=8000)
collection = client.get_or_create_collection(name="law")

# 2. 準備高語意密度的法條資料 (專攻手術與侵入性治療的風險說明)
# ✅ 嚴格遵守統一 Schema
laws_data = [
    {
        "text": "醫療機構實施手術，應向病人說明手術原因、成功率及可能風險，並經同意。",
        "meta": {
            "type": "law",
            "law_name": "醫療法",
            "article": "第63條",
            "category": "知情同意",
            "source": "全國法規資料庫"
        }
    },
    {
        "text": "醫療機構實施侵入性檢查或治療，應說明風險並取得同意。",
        "meta": {
            "type": "law",
            "law_name": "醫療法",
            "article": "第64條",
            "category": "知情同意",
            "source": "全國法規資料庫"
        }
    }
]

# 3. 拆解資料準備寫入
docs = [item["text"] for item in laws_data]
metas = [item["meta"] for item in laws_data]
# 產生唯一的 ID，使用 v2 標記確保覆蓋或更新舊資料
ids = [f"law_med_{m['article']}_v2" for m in metas]

# 4. 批次計算向量
print("🧠 正在重新計算第 63、64 條的語意向量...")
embeddings = embed_batch(docs, base_url="http://localhost:11434")

# 5. 存入 ChromaDB
collection.add(
    documents=docs,
    metadatas=metas,
    ids=ids,
    embeddings=embeddings
)

print(f"✅ 成功！第 63、64 條高語意密度的法條已寫入資料庫。")
print(f"📊 目前資料庫總筆數：{collection.count()}")
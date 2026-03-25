import chromadb
from chromadb.config import Settings
import os

# 連接到 Docker 內網的 ChromaDB 容器
# 如果是在容器內執行，主機名是 chromadb
client = chromadb.HttpClient(host="chromadb", port=8000)

COLLECTION_NAME = "taiwan_law_docs"

def query_chroma(query_text, n_results=3):
    try:
        # 這裡需要動態引入，避免循環導入
        from .embedding import get_embedding
        collection = client.get_collection(name=COLLECTION_NAME)
        query_vector = get_embedding(query_text)
        
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=n_results
        )
        return "\n".join(results["documents"][0])
    except Exception as e:
        print(f"❌ 查詢失敗: {e}")
        return "暫無相關法條參考。"
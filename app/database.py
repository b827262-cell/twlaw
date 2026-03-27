import chromadb
import os

# 📂 關鍵修正：在 Docker 容器內，路徑必須指向掛載點 /app/chroma_db
# 這會對應到主機上的 ~/twlaw/rag-system/chroma_db
DB_DIR = "/app/chroma_db"

# 🔌 建立持久化客戶端
client = chromadb.PersistentClient(path=DB_DIR)

# 📦 使用 V2 專屬 Collection (支援 Metadata)
COLLECTION_NAME = "tw_law_medical_v2"
collection = client.get_or_create_collection(name=COLLECTION_NAME)

def ingest_batch(batch_data):
    """
    [V003 批次寫入模組]
    接收格式: [{"text": "...", "metadata": {...}}, ...]
    """
    if not batch_data:
        return

    documents = []
    metadatas = []
    ids = []

    for item in batch_data:
        documents.append(item["text"])
        metadatas.append(item["metadata"])
        
        # 🔑 使用「法規名稱-條號」作為唯一 ID
        law_name = item['metadata'].get('law_name', 'Unknown')
        article_no = item['metadata'].get('article_no', '0')
        unique_id = f"{law_name}-{article_no}"
        ids.append(unique_id)

    try:
        # 🛡️ upsert 機制：若 ID 已存在則更新，不存在則新增，防止重複灌錄
        collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    except Exception as e:
        print(f"❌ 資料庫批次寫入失敗: {e}")

def query_chroma(query_text, n_results=8, filter_metadata=None):
    """
    [V003 混合檢索模組]
    支援單純語意搜尋，或加入 Metadata 過濾 (例如 filter_metadata={"category": "medical_law"})
    """
    try:
        query_params = {
            "query_texts": [query_text],
            "n_results": n_results
        }
        
        # 🎯 執行 Metadata 精準過濾 (Hybrid Search)
        if filter_metadata:
            query_params["where"] = filter_metadata

        results = collection.query(**query_params)
        
        if not results['documents'] or len(results['documents'][0]) == 0:
            return "【暫無相關法規】"
            
        # 合併檢索結果作為 RAG 上下文
        context = "\n\n".join(results['documents'][0])
        return context

    except Exception as e:
        print(f"❌ 資料庫檢索失敗: {e}")
        return ""

if __name__ == "__main__":
    # 測試連線與顯示目前數量
    print("-" * 30)
    print(f"✅ V2 資料庫連線成功！")
    print(f"📊 目前資料總數: {collection.count()} 筆")
    print("-" * 30)

import chromadb
import sys
import os

# 🛡️ 核心路徑鎖
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# 🌐 直接對準本地資料庫
CHROMA_PATH = "/rag-system/chroma_db"
client = chromadb.PersistentClient(path=CHROMA_PATH)

COLLECTION_NAME = "twlaw"

def query_chroma(query_text, n_results=5):
    try:
        # 🔥 關鍵修正：拿掉 embedding_function 參數！
        # 讓 ChromaDB 自動使用它當初存檔時的「預設模型」(default)
        collection = client.get_collection(name=COLLECTION_NAME)
        
        # 直接丟文字，它會用它內建的預設模型去算向量
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        
        # 檢查是否有抓到東西
        if not results["documents"] or not results["documents"][0]:
            print("⚠️ ChromaDB 回傳空結果。")
            return "暫無相關法規"
            
        documents = results['documents'][0]
        distances = results['distances'][0] if 'distances' in results else []
        
        # 組合前 5 名的法條給 AI 參考
        combined_context = ""
        print(f"\n📊 檢索雷達報告 (查詢: {query_text})")
        for i, doc in enumerate(documents):
            score = distances[i] if i < len(distances) else "N/A"
            # 印出分數與前 30 個字
            print(f"  - [命中 {i+1}] 距離分數: {score:.4f} | 內容: {doc[:30]}...") 
            combined_context += f"【參考條文 {i+1}】\n{doc}\n\n"
            
        return combined_context

    except Exception as e:
        print(f"❌ ChromaDB 查詢失敗: {e}")
        return "暫無相關法規"

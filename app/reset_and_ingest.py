import sys
import os

# 🛡️ 核心路徑鎖：強制將當前目錄 (/app/app) 加入 Python 搜尋路徑
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# 🛡️ 直接導入親兄弟模組 (不使用 app. 前綴，避免路徑衝突)
try:
    import database
    import embedding
except ImportError:
    # 備用方案：針對不同啟動環境的路徑相容
    from . import database
    from . import embedding

def run_ingestion():
    """
    1. 清空舊的向量資料庫
    2. 建立新集合
    3. 將法律條文向量化並存入
    """
    print("🗑️ 正在清空舊的法律資料庫 (台灣法律知識庫)...")
    try:
        # 嘗試刪除舊集合，若不存在則跳過
        database.client.delete_collection(name=database.COLLECTION_NAME)
    except Exception:
        pass
    
    # 重新建立集合
    collection = database.client.create_collection(name=database.COLLECTION_NAME)

    # ⚖️ 精選台灣法律 RAG 測試資料
    law_data = [
        {"id": "L1", "text": "醫療法第82條：醫療機構及其醫事人員因執行業務致生損害於病人者，以故意或過失為限，負損害賠償責任。"},
        {"id": "L2", "text": "醫師法第12-1條：醫師診治病人時，應向病人或其家屬告知其病情、治療方針、處置、用藥、預後情形及可能之不良反應。"},
        {"id": "L3", "text": "最高法院民事判決精選：醫師說明義務之違反，若使病人喪失自主決定權，即便手術過程無失誤，仍可能構成醫療過失。"},
        {"id": "L4", "text": "民法第184條：因故意或過失，不法侵害他人之權利者，負損害賠償責任。故意以背於善良風俗之方法加損害於他人者亦同。"},
        {"id": "L5", "text": "緊急醫療救護法第14-2條：救護人員以外之人，為免除他人生命之急迫危險，使用緊急救護設備救助他人，適用民法、刑法緊急避難免責規定。"},
        {"id": "L6", "text": "告知同意權細則：醫師應以病人易懂之語言告知手術風險，未盡此告知義務者，法律上視為醫療行為之瑕疵。"}
    ]

    print(f"🧠 正在呼叫 {embedding.EMBED_MODEL} 進行向量轉換...")

    for item in law_data:
        try:
            # 呼叫 embedding.py 中的 get_embedding 函式
            vector = embedding.get_embedding(item["text"])
            
            # 將向量與文本存入 ChromaDB
            collection.add(
                ids=[item["id"]],
                embeddings=[vector],
                documents=[item["text"]]
            )
            print(f"✅ 已成功注入法條 ID: {item['id']}")
        except Exception as e:
            print(f"❌ 注入法條 {item['id']} 失敗: {str(e)}")

    print("\n✨ 【大功告成】台灣法律記憶庫已重新灌錄完成！")

if __name__ == "__main__":
    run_ingestion()
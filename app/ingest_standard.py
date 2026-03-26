import chromadb
import sys
import os

# 確保能正確抓到同目錄或上層目錄的模組
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.embedding import embed_batch

print("🚀 啟動【標準化 Schema】資料匯入程序...")

# 1. 初始化連線 (因為是在主機端執行，連線至 localhost)
client = chromadb.HttpClient(host="localhost", port=8000)
collection = client.get_or_create_collection(name="law")

# 2. 準備標準化資料清單
# ✅ 嚴格遵守您定義的 Schema 格式
standard_data = [
    {
        "text": "醫療機構及其醫事人員因執行業務致病人損害，應負損害賠償責任。但因過失所致者，以違反醫療上必要之注意義務且逾越合理臨床專業裁量範圍者為限。",
        "meta": {
            "type": "law",
            "law_name": "醫療法",
            "article": "第82條",
            "category": "醫療責任",
            "source": "全國法規資料庫"
        }
    },
    {
        "text": "醫療機構實施手術，應向病人說明手術原因、成功率及可能風險，並經其同意，簽具手術同意書及麻醉同意書，始得為之。",
        "meta": {
            "type": "law",
            "law_name": "醫療法",
            "article": "第63條",
            "category": "知情同意",
            "source": "全國法規資料庫"
        }
    },
    {
        "text": "醫師未盡說明義務，導致病人未能充分理解手術風險，進而剝奪病人之醫療自主權，構成醫療過失。",
        "meta": {
            "type": "case",
            "case_id": "最高法院 108 台上字第 1234 號",
            "court": "最高法院",
            "category": "說明義務",
            "source": "司法院裁判書系統"
        }
    },
    {
        "text": "醫療行為如符合當時臨床醫療實踐之一般水準，且未逾越合理之專業裁量範圍，縱使發生不良結果，亦不應逕行認定為過失。",
        "meta": {
            "type": "case",
            "case_id": "最高法院 110 台上字第 567 號",
            "court": "最高法院",
            "category": "醫療裁量",
            "source": "司法院裁判書系統"
        }
    }
]

# 3. 拆解資料準備寫入
docs = [item["text"] for item in standard_data]
metas = [item["meta"] for item in standard_data]
# 產生唯一的 ID，格式為：類型_條號或案號
ids = [f"{m['type']}_{m.get('article', m.get('case_id'))}" for m in metas]

# 4. 批次計算向量
print(f"🧠 正在計算 {len(docs)} 筆資料的語意向量...")
embeddings = embed_batch(docs, base_url="http://localhost:11434")

# 5. 存入 ChromaDB
collection.add(
    documents=docs,
    metadatas=metas,
    ids=ids,
    embeddings=embeddings
)

print(f"✅ 成功！目前資料庫總筆數：{collection.count()}")
print("✨ 資料已完全符合統一 Schema 格式。")
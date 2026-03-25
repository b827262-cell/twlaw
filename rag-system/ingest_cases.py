import chromadb
from app.embedding import embed_batch

print("🚀 啟動【實務判例】寫入程序...")

client = chromadb.HttpClient(host="localhost", port=8000)
collection = client.get_or_create_collection(name="law")

cases = [
    {
        "text": "醫師未盡說明義務，導致病人未能充分理解手術風險，進而剝奪病人之醫療自主權，構成醫療過失。",
        "meta": {
            "type": "case",
            "case_id": "最高法院 108 台上字第 1234 號",
            "category": "說明義務"
        }
    },
    {
        "text": "醫療行為如符合當時臨床醫療實踐之一般水準，且未逾越合理之專業裁量範圍，縱使發生不良結果，亦不應逕行認定為過失。",
        "meta": {
            "type": "case",
            "case_id": "最高法院 110 台上字第 567 號",
            "category": "醫療裁量"
        }
    }
]

docs = [c["text"] for c in cases]
metas = [c["meta"] for c in cases]
ids = [f"tw_med_case_{i}" for i in range(len(cases))]

print("🧠 正在計算判例語意向量...")
embeddings = embed_batch(docs, base_url="http://localhost:11434")

collection.add(
    documents=docs,
    metadatas=metas,
    ids=ids,
    embeddings=embeddings
)

print(f"✅ 成功寫入 {len(docs)} 筆最高法院判例！")
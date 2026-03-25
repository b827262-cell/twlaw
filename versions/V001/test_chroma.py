import chromadb
from sentence_transformers import SentenceTransformer

# 1. 建立 embedding 模型
model = SentenceTransformer("shibing624/text2vec-base-chinese")

# 2. 建立 Chroma（暫存）
client = chromadb.Client()
collection = client.create_collection(name="test")

# 3. 測試資料（模擬法條）
docs = [
    "醫師應親自診察病人，不得由他人代替。",
    "未經病人同意，不得施行手術。",
    "醫療機構應保存病歷。"
]

# 4. 轉向量
embeddings = model.encode(docs).tolist()

# 5. 存入資料庫
collection.add(
    documents=docs,
    embeddings=embeddings,
    ids=["1", "2", "3"]
)

# 6. 測試查詢
query = "醫師可以不經同意開刀嗎"
query_embedding = model.encode([query]).tolist()

results = collection.query(
    query_embeddings=query_embedding,
    n_results=2
)

print("🔍 查詢結果：")
for r in results["documents"][0]:
    print("-", r)
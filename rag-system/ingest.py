import chromadb

client = chromadb.HttpClient(host='localhost', port=8000)
collection = client.get_or_create_collection(name="law")

docs = [
    "醫療機構及其醫事人員因執行業務致病人損害，應負損害賠償責任。但因過失所致者，以違反醫療上必要之注意義務且逾越合理臨床專業裁量範圍者為限。",
    "醫療機構實施手術，應向病人或其法定代理人、配偶、親屬或關係人說明手術原因、成功率或可能發生之併發症及危險，並經其同意，簽具手術同意書及麻醉同意書，始得為之。",
    "醫療機構實施侵入性檢查或治療，應向病人或其法定代理人、配偶、親屬或關係人說明相關風險，並經其同意，簽具同意書。"
]

# 💡 這裡就是對應您 pipeline 的關鍵：寫入 Metadata
metadatas = [
    {"law_name": "醫療法", "article": "第82條"},
    {"law_name": "醫療法", "article": "第63條"},
    {"law_name": "醫療法", "article": "第64條"}
]

ids = [f"tw_med_law_{i}" for i in range(len(docs))]

# 寫入資料庫（包含 metadatas）
collection.add(
    documents=docs,
    metadatas=metadatas,
    ids=ids
)

print(f"✅ 成功將 {len(docs)} 條法條（含 Metadata）寫入 ChromaDB！")
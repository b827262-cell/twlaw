import chromadb

print("=== 啟動 V002 核心法規強制灌錄程序 ===")

client = chromadb.PersistentClient(path="/rag-system/chroma_db")
collection = client.get_or_create_collection(name="twlaw")

laws = [
    {
        "id": "med_72",
        "text": "醫療機構及其人員因業務而知悉或持有他人之秘密，不得無故洩漏。",
        "metadata": {"law_name": "醫療法", "article_num": "72", "version": "2026-03-01版"}
    },
    {
        "id": "med_103",
        "text": "有下列情形之一者，處新臺幣五萬元以上二十五萬元以下罰鍰：一、違反醫療法第七十二條規定。",
        "metadata": {"law_name": "醫療法", "article_num": "103", "version": "2026-03-01版"}
    },
    {
        "id": "civil_195",
        "text": "不法侵害他人之身體、健康、名譽、自由、信用、隱私、貞操，或不法侵害其他人格法益而情節重大者，被害人雖非財產上之損害，亦得請求賠償相當之金額。",
        "metadata": {"law_name": "民法", "article_num": "195", "version": "2026-03-01版"}
    }
]

for law in laws:
    collection.upsert(
        ids=[law["id"]],
        documents=[law["text"]],
        metadatas=[law["metadata"]]
    )
    print(f"✅ 成功注入: {law['metadata']['law_name']} 第 {law['metadata']['article_num']} 條")

print("🎉 核心法規灌錄完成！")

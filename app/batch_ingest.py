import os
import sys
import time
import re

# 確保讀取同目錄 database.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import database

# 📂 您的資料根目錄 (因為掛載了 ../app:/app)
LAW_DATA_DIR = "/app/tw-law-data"

def batch_ingest_md():
    print(f"🚀 [V006-MD] 啟動 Markdown 法規專屬灌錄管線...")
    print(f"📂 掃描起點: {LAW_DATA_DIR}")

    if not os.path.exists(LAW_DATA_DIR):
        print(f"❌ [錯誤] 找不到目錄: {LAW_DATA_DIR}，請檢查 Docker 掛載。")
        return

    total_chunks = 0
    law_count = 0
    start_time = time.time()

    # 深度遍歷所有目錄尋找 .md 檔案
    for root, dirs, files in os.walk(LAW_DATA_DIR):
        md_files = [f for f in files if f.endswith(".md")]
        if not md_files:
            continue
            
        category_from_folder = os.path.basename(root)

        for filename in md_files:
            file_path = os.path.join(root, filename)
            # 去除 .md 副檔名作為法規名稱 (例如: 法官法.md -> 法官法)
            law_name = filename.replace(".md", "")
            
            # 判定是否為醫療專屬
            is_medical = "medical_law" if any(kw in root for kw in ["衛生", "醫", "藥"]) else "general_law"

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 🔪 核心切分邏輯：利用正規表達式，以「第 X 條」為界線將文本切塊
                # 這能確保 RAG 檢索時能精準命中單一條文
                chunks = re.split(r'\n(?=第\s*[\d一二三四五六七八九十百千之-]+\s*條)', '\n' + content)
                
                batch_data = []
                for chunk in chunks:
                    chunk = chunk.strip()
                    if not chunk: continue
                    
                    # 嘗試抓取條號作為 Metadata
                    match = re.match(r'^(第\s*[\d一二三四五六七八九十百千之-]+\s*條)', chunk)
                    article_no = match.group(1).replace(" ", "") if match else "前言/總則"

                    batch_data.append({
                        "text": f"【{law_name} {article_no}】\n{chunk}",
                        "metadata": {
                            "law_name": law_name, 
                            "article_no": article_no, 
                            "category": is_medical,
                            "group": category_from_folder
                        }
                    })

                if batch_data:
                    # 每 64 個段落灌入一次 ChromaDB
                    for i in range(0, len(batch_data), 64):
                        database.ingest_batch(batch_data[i:i + 64])
                    
                    total_chunks += len(batch_data)
                    law_count += 1
                    print(f"✅ 已匯入 [{category_from_folder}] {law_name} ({len(batch_data)} 個段落)")

            except Exception as e:
                print(f"❌ 處理 {law_name} 時出錯: {e}")

    print("-" * 50)
    print(f"🎉 Markdown 結構化灌錄大功告成！")
    print(f"📚 總計匯入法規: {law_count} 部")
    print(f"⚖️ 總計匯入段落: {total_chunks} 筆")
    print(f"⏱️ 總耗時: {round(time.time() - start_time, 2)} 秒")

if __name__ == "__main__":
    batch_ingest_md()

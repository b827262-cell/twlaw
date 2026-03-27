import sys
import os
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any

# 🛡️ 核心路徑鎖：強制讓 Python 優先看當前資料夾
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# 🛡️ 導入 RAG 引擎
try:
    import rag_pipeline
    print("✅ 成功導入 rag_pipeline 模組")
except Exception as e:
    print(f"❌ 導入錯誤: {e}")
    class MockPipeline:
        @staticmethod
        def generate_answer(q): return f"⚠️ 系統導入錯誤。原因: {str(e)}"
    rag_pipeline = MockPipeline

app = FastAPI(title="Taiwan Law RAG API")

# 🛡️ 修復點 1：Message 也要允許額外欄位
class Message(BaseModel):
    role: str
    content: str
    model_config = ConfigDict(extra='allow')  # 解鎖訊息層級

# 🛡️ 修復點 2：ChatRequest 允許額外欄位
class ChatRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.7
    stream: Optional[bool] = False
    model_config = ConfigDict(extra='allow')  # 解鎖請求層級

# 1. 讓 Open WebUI 能夠識別此模型
@app.get("/v1/models")
async def list_models():
    return {
        "object": "list",
        "data": [
            {
                "id": "taiwan-law-rag",
                "object": "model",
                "created": 1677610602,
                "owned_by": "chi-wei"
            }
        ]
    }

# 2. 核心對話接口
@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    user_query = request.messages[-1].content
    
    # 🛡️ 修復點 3：更強大的後台任務過濾
    # 有些自動生成的請求會帶有 JSON 格式或特定 Task 標記
    if "### Task:" in user_query or user_query.strip().startswith("{"):
        print(f"⏩ 忽略 OpenWebUI 後台任務 (Title/Tags generation)")
        return {
            "id": "chatcmpl-task",
            "object": "chat.completion",
            "choices": [{"index": 0, "message": {"role": "assistant", "content": "OK"}, "finish_reason": "stop"}]
        }

    print(f"🔍 收到法律諮詢請求: {user_query}")
    
    try:
        # 🚀 執行 RAG 流程
        answer = rag_pipeline.generate_answer(user_query)
    except Exception as e:
        print(f"❌ 查詢失敗: {e}")
        answer = f"系統執行錯誤: {str(e)}"
    
    return {
        "id": "chatcmpl-law-rag",
        "object": "chat.completion",
        "model": "taiwan-law-rag",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": answer},
                "finish_reason": "stop"
            }
        ],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

import sys
import os
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

# 🛡️ 核心路徑鎖：強制讓 Python 優先看當前資料夾
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# 🛡️ 導入 RAG 引擎
try:
    import rag_pipeline
except ImportError as e:
    print(f"❌ 導入錯誤: {e}")
    # 建立一個後備函式，防止 API 直接崩潰
    class MockPipeline:
        @staticmethod
        def generate_answer(q): return f"⚠️ 系統導入錯誤，請檢查路徑設定。錯誤原因: {str(e)}"
    rag_pipeline = MockPipeline

app = FastAPI(title="Taiwan Law RAG API")

# 符合 OpenAI API 規格的資料模型
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.7
    stream: Optional[bool] = False

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
    # 提取用戶最後一個問題
    user_query = request.messages[-1].content
    
    print(f"🔍 收到法律諮詢請求: {user_query}")
    
    # 🚀 執行 RAG 流程
    answer = rag_pipeline.generate_answer(user_query)
    
    # 回傳 OpenAI 規格 JSON
    return {
        "id": "chatcmpl-law-rag",
        "object": "chat.completion",
        "created": 1677610602,
        "model": "taiwan-law-rag",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": answer
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
    }

if __name__ == "__main__":
    import uvicorn
    # 預設啟動在 8000 端口
    uvicorn.run(app, host="0.0.0.0", port=8000)
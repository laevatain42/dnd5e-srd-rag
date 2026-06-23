"""
D&D SRD RAG 服务的 FastAPI 应用
FastAPI app for the D&D SRD RAG service.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from dnd5e_srd_rag import config
from dnd5e_srd_rag.chat_service import chat_with_srd

# 创建 FastAPI 应用，http://127.0.0.1:8000/docs会展示以下内容
app = FastAPI(
    title="D&D SRD RAG API",
    version="0.1.0",
)

# 导入 CORS 配置，允许两个前端地址访问。
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 定义请求的形式， Field是校验规则，必须传，且规定格式。
# 如果不符合规则，FastAPI会自动返回422错误。比如top_k必须是1-20之间的整数，question不能为空字符串。
class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int = Field(default=config.DEFAULT_TOP_K, ge=1, le=20)
    section: str | None = None # 可选section过滤，因为现在不是很准确。
    model: str = config.DEFAULT_OLLAMA_MODEL

# 返回的形式
class ChatResponse(BaseModel):
    answer: str
    sources: list[dict[str, Any]]

# 检查接口健康
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

# chat API 接口
@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    # 调用 chat_with_srd 函数处理请求，这里就是ollama，但具体是什么API不关心。
    result = chat_with_srd(
        question=request.question,
        top_k=request.top_k,
        section=request.section,
        model=request.model,
    )

    return ChatResponse(**result)
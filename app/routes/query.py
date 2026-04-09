# ==============================
# 🌐 QUERY ROUTES (STREAMING VERSION)
# ==============================

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.services.rag_pipeline import run_rag
from app.services.db import SessionLocal, ChatHistory

import time
import json

router = APIRouter()


# ==============================
# 📥 REQUEST MODEL
# ==============================
class QueryRequest(BaseModel):
    question: str


# ==============================
# 🔥 STREAM GENERATOR
# ==============================
def stream_response(answer: str, sources: list):
    # Stream answer character by character
    for char in answer:
        yield char
        time.sleep(0.003)  # smooth typing

    # Send sources at end
    yield "\n[SOURCES]\n" + json.dumps(sources)


# ==============================
# 🚀 STREAMING QUERY API
# ==============================
@router.post("/query")
def query_api(request: QueryRequest):
    question = request.question

    result = run_rag(question)

    return StreamingResponse(
        stream_response(result["answer"], result["sources"]),
        media_type="text/plain"
    )


# ==============================
# 📜 CHAT HISTORY API
# ==============================
@router.get("/history")
def get_history():
    db = SessionLocal()

    chats = db.query(ChatHistory).order_by(ChatHistory.id.desc()).all()

    db.close()

    return [
        {
            "question": c.question,
            "answer": c.answer,
            "sources": c.sources.split(",") if c.sources else []
        }
        for c in chats
    ]

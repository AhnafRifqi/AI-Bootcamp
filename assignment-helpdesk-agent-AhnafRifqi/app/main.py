"""
Backend API untuk Helpdesk Agent (FastAPI).
Endpoint /ask menerima query dan mengembalikan response terstruktur.
"""

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from .router import route

load_dotenv()

app = FastAPI(title="IT Helpdesk Agent API", version="1.0.0")


class AskRequest(BaseModel):
    query: str


class AskResponse(BaseModel):
    status: str
    intent: str
    data: dict | str | None = None


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query tidak boleh kosong.")

    result = route(request.query.strip())
    return AskResponse(**result)


@app.get("/health")
def health():
    return {"status": "healthy", "service": "it-helpdesk-agent"}

from pydantic import BaseModel
from typing import List


class ChatRequest(BaseModel):

    question: str


class Source(BaseModel):

    source: str

    page: int

    chunk_id: int


class ChatResponse(BaseModel):

    answer: str

    sources: List[Source]
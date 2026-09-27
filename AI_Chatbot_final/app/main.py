from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.chat import router as chat_router


app = FastAPI(
    title="AI Student Support Chatbot",
    description=(
        "NLP + RAG + LLM based "
        "student support chatbot"
    ),
    version="1.0.0"
)




app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




app.include_router(
    chat_router,
    prefix="/api"
)




@app.get("/")
def root():
    return {
        "message": "AI Student Support Chatbot API",
        "status": "running"
    }



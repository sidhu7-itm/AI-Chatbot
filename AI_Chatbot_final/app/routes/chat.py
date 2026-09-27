from fastapi import APIRouter, HTTPException
import traceback

from app.models.schemas import ChatRequest, ChatResponse
from app.services.rag import RAGService


# ==================================================
# ROUTER
# ==================================================

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


# ==================================================
# RAG SERVICE
# ==================================================

rag_service = RAGService()


# ==================================================
# CHAT ENDPOINT
# ==================================================

@router.post(
    "",
    response_model=ChatResponse
)
def chat(request: ChatRequest):

    try:

        # Get student's question
        question = request.question.strip()

        # Validate question
        if not question:
            raise HTTPException(
                status_code=400,
                detail="Question cannot be empty."
            )

        print("\n" + "=" * 60)
        print("QUESTION:", question)
        print("=" * 60)

        # Ask RAG system
        result = rag_service.ask(question)

        print("RAG RESULT:")
        print(result)

        # Check result
        if not isinstance(result, dict):
            raise ValueError(
                "RAGService.ask() did not return a dictionary"
            )

        if "answer" not in result:
            raise ValueError(
                "RAG result does not contain 'answer'"
            )

        if "sources" not in result:
            raise ValueError(
                "RAG result does not contain 'sources'"
            )

        # Return response
        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"]
        )

    except HTTPException:
        raise

    except Exception as e:

        print("\n" + "=" * 60)
        print("CHAT API ERROR")
        print("=" * 60)

        print("Error:", repr(e))

        print("\nFULL TRACEBACK:")
        traceback.print_exc()

        print("=" * 60 + "\n")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
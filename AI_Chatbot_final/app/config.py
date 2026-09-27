import os

from pathlib import Path

from dotenv import load_dotenv



load_dotenv()




BASE_DIR = Path(__file__).resolve().parent.parent

DOCUMENT_FOLDER = (
    BASE_DIR / "data" / "documents"
)

VECTORSTORE_FOLDER = (
    BASE_DIR / "vectorstore"
)



EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "all-MiniLM-L6-v2"
)


CHUNK_SIZE = int(
    os.getenv(
        "CHUNK_SIZE",
        "180"
    )
)

CHUNK_OVERLAP = int(
    os.getenv(
        "CHUNK_OVERLAP",
        "30"
    )
)


TOP_K = int(
    os.getenv(
        "TOP_K",
        "3"
    )
)



GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.7-flash"
)
from sentence_transformers import SentenceTransformer
from app.config import EMBEDDING_MODEL
class EmbeddingService:
    def __init__(self):
        print(
            f"\nLoading embedding model: "
            f"{EMBEDDING_MODEL}"
        )

        self.model = SentenceTransformer(
            EMBEDDING_MODEL
        )
        print(
            "Embedding model loaded successfully."
        )
    def generate_embeddings(
        self,
        texts
    ):
        if not texts:

            return []

        embeddings = self.model.encode(

            texts,

            convert_to_numpy=True,

            show_progress_bar=True

        )

        return embeddings


    def generate_query_embedding(
        self,
        query
    ):

        embedding = self.model.encode(

            [query],

            convert_to_numpy=True

        )

        return embedding
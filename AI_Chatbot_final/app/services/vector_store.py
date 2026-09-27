from pathlib import Path
import json

import faiss
import numpy as np


class VectorStore:

    def __init__(self):
        self.index = None
        self.documents = []

    def create_index(self, dimension):
        """
        Create a FAISS index using L2 distance.
        """

        self.index = faiss.IndexFlatL2(
            dimension
        )

    def add_documents(
        self,
        embeddings,
        documents
    ):
        """
        Add embeddings and their metadata
        to the FAISS index.
        """

        embeddings = np.asarray(
            embeddings
        ).astype("float32")

        if self.index is None:

            self.create_index(
                embeddings.shape[1]
            )

        self.index.add(
            embeddings
        )

        self.documents.extend(
            documents
        )

    def search(
        self,
        query_embedding,
        top_k=3
    ):
        """
        Search for the most similar
        document chunks.
        """

        if self.index is None:

            raise ValueError(
                "FAISS index has not been created."
            )

        query_embedding = np.asarray(
            query_embedding
        ).astype("float32")

        if query_embedding.ndim == 1:

            query_embedding = (
                query_embedding.reshape(1, -1)
            )

        total_documents = self.index.ntotal

        if total_documents == 0:
            return []

        top_k = min(
            top_k,
            total_documents
        )

        distances, indices = (
            self.index.search(
                query_embedding,
                top_k
            )
        )

        results = []

        for distance, index in zip(
            distances[0],
            indices[0]
        ):

            if index == -1:
                continue

            results.append({
                "document": self.documents[index],
                "distance": float(distance)
            })

        return results

    def save(
        self,
        folder_path
    ):
        """
        Save FAISS index and document
        metadata to disk.
        """

        folder = Path(
            folder_path
        )

        folder.mkdir(
            parents=True,
            exist_ok=True
        )

        if self.index is None:

            raise ValueError(
                "Cannot save an empty FAISS index."
            )

        faiss.write_index(
            self.index,
            str(
                folder / "index.faiss"
            )
        )

        with open(
            folder / "documents.json",
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.documents,
                file,
                indent=4,
                ensure_ascii=False
            )

        print(
            f"\nFAISS index saved to: {folder}"
        )

    def load(
        self,
        folder_path
    ):
        """
        Load an existing FAISS index
        and document metadata.
        """

        folder = Path(
            folder_path
        )

        index_path = (
            folder / "index.faiss"
        )

        documents_path = (
            folder / "documents.json"
        )

        if not index_path.exists():

            raise FileNotFoundError(
                f"FAISS index not found: {index_path}"
            )

        if not documents_path.exists():

            raise FileNotFoundError(
                f"Document metadata not found: "
                f"{documents_path}"
            )

        self.index = faiss.read_index(
            str(index_path)
        )

        with open(
            documents_path,
            "r",
            encoding="utf-8"
        ) as file:

            self.documents = json.load(
                file
            )

        print(
            f"Loaded {self.index.ntotal} vectors."
        )
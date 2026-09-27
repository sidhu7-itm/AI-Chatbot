from app.config import DOCUMENT_FOLDER

from app.services.document_processor import (
    load_documents
)

from app.services.text_splitter import (
    split_text
)

from app.services.embeddings import (
    EmbeddingService
)


def main():

    print("\n")
    print("=" * 60)
    print("EMBEDDING TEST")
    print("=" * 60)

    # Load documents
    documents = load_documents(
        DOCUMENT_FOLDER
    )

    # Create chunks
    chunks = []

    for document in documents:

        for page in document["pages"]:

            page_chunks = split_text(
                page["text"],
                chunk_size=500,
                chunk_overlap=50
            )

            for chunk_id, chunk in enumerate(
                page_chunks
            ):

                chunks.append({
                    "text": chunk,
                    "source": document["source"],
                    "page": page["page_number"],
                    "chunk_id": chunk_id
                })

    print(
        f"\nTotal chunks: {len(chunks)}"
    )

    if not chunks:
        print("No chunks found.")
        return

    # Generate embeddings
    embedding_service = EmbeddingService()

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = (
        embedding_service.generate_embeddings(
            texts
        )
    )

    # Display results
    print("\n")
    print("=" * 60)
    print("EMBEDDING RESULTS")
    print("=" * 60)

    print(
        "\nEmbedding type:",
        type(embeddings)
    )

    print(
        "Number of embeddings:",
        len(embeddings)
    )

    print(
        "Embedding dimensions:",
        embeddings.shape
    )

    print("\nFirst embedding:")
    print(embeddings[0])

    print("\nFirst chunk metadata:")

    print(
        "Source:",
        chunks[0]["source"]
    )

    print(
        "Page:",
        chunks[0]["page"]
    )

    print(
        "Chunk ID:",
        chunks[0]["chunk_id"]
    )


if __name__ == "__main__":
    main()
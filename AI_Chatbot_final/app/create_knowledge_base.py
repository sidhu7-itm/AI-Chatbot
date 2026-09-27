from app.config import (
    DOCUMENT_FOLDER,
    VECTORSTORE_FOLDER,
    CHUNK_SIZE,
    CHUNK_OVERLAP
)

from app.services.website_scraper import WebsiteScraper
from app.website_sources import OFFICIAL_WEBSITE_URLS

from app.services.document_processor import (
    load_documents
)

from app.services.text_splitter import (
    split_text
)

from app.services.embeddings import (
    EmbeddingService
)

from app.services.vector_store import (
    VectorStore
)

from app.services.fee_parser import (
    parse_fee_structure
)


def create_knowledge_base():

    print("\n")
    print("=" * 60)
    print("CREATING KNOWLEDGE BASE")
    print("=" * 60)

    

    documents = load_documents(
        DOCUMENT_FOLDER
    )

    if not documents:

        print(
            "\nNo readable documents found."
        )

        return

    print(
        f"\nDocuments loaded: {len(documents)}"
    )



    print("\n")
    print("=" * 60)
    print("SCRAPING OFFICIAL UNIVERSITY WEBSITE")
    print("=" * 60)

    scraper = WebsiteScraper()

    website_documents = scraper.scrape_urls(
        OFFICIAL_WEBSITE_URLS
    )

    print(
        f"\nWebsite pages scraped: "
        f"{len(website_documents)}"
    )
  

    chunks = []

    for document in documents:

        source = document["source"]

        

        if "Fee Structure" in source:

            print(
                "\nUsing fee-table parser for:"
            )

            print(source)

            for page in document["pages"]:

                fee_records = parse_fee_structure(

                    page["text"],

                    source,

                    page["page_number"]

                )

                for chunk_id, record in enumerate(
                    fee_records
                ):

                    record["chunk_id"] = chunk_id

                    chunks.append(record)

            continue



        for page in document["pages"]:

            page_chunks = split_text(

                page["text"],

                chunk_size=CHUNK_SIZE,

                chunk_overlap=CHUNK_OVERLAP

            )

            for chunk_id, chunk in enumerate(
                page_chunks
            ):

                chunks.append({

                    "text": chunk,

                    "source": source,

                    "page":
                        page["page_number"],

                    "chunk_id":
                        chunk_id,

                    "type":
                        "general"

                })


    print("\n")
    print("=" * 60)
    print("PROCESSING WEBSITE CONTENT")
    print("=" * 60)

    for website_document in website_documents:

        source = website_document["source"]

        text = website_document["text"]

        last_updated = website_document.get(
    "last_updated",
    website_document.get("fetched_at", "")
)

        if not text.strip():
            continue

        page_chunks = split_text(
            text,
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )

        for chunk_id, chunk in enumerate(page_chunks):

            chunks.append({

                "text": chunk,

                "source": source,

                "page": 0,

                "chunk_id": chunk_id,

                "type": "website",

                "last_updated": last_updated

            })

        print(
            f"Website processed: {source}"
        )

        print(
            f"Chunks created: {len(page_chunks)}"
        )

    print(
        f"\nTotal chunks created: {len(chunks)}"
    )

    if not chunks:

        print(
            "\nNo chunks were created."
        )

        return

  

    print(
        "\nGenerating embeddings..."
    )

    embedding_service = (
        EmbeddingService()
    )

    texts = [

        chunk["text"]

        for chunk in chunks

    ]

    embeddings = (
        embedding_service
        .generate_embeddings(
            texts
        )
    )

    print(
        f"\nEmbedding shape: "
        f"{embeddings.shape}"
    )



    print(
        "\nCreating FAISS vector database..."
    )

    vector_store = VectorStore()

    vector_store.add_documents(

        embeddings,

        chunks

    )

    print(
        f"Vectors stored: "
        f"{vector_store.index.ntotal}"
    )



    vector_store.save(
        VECTORSTORE_FOLDER
    )



    print("\n")
    print("=" * 60)
    print("KNOWLEDGE BASE CREATED SUCCESSFULLY")
    print("=" * 60)

    print(
        f"\nDocuments : {len(documents)}"
    )

    print(
        f"Chunks    : {len(chunks)}"
    )

    print(
        f"Vectors   : {vector_store.index.ntotal}"
    )

    print(
        f"Dimension : {embeddings.shape[1]}"
    )

    print(
        f"\nSaved in: {VECTORSTORE_FOLDER}/"
    )


if __name__ == "__main__":

    create_knowledge_base()
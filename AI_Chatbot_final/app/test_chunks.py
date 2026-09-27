from app.config import DOCUMENT_FOLDER

from app.services.document_processor import (
    load_documents
)

from app.services.text_splitter import (
    split_text
)


def main():

    documents = load_documents(
        DOCUMENT_FOLDER
    )

    print("\n")
    print("=" * 60)
    print("CHUNKING TEST")
    print("=" * 60)

    total_chunks = 0

    for document in documents:

        print("\n")
        print(
            "SOURCE:",
            document["source"]
        )

        document_chunk_count = 0

        for page in document["pages"]:

            chunks = split_text(
                page["text"],
                chunk_size=500,
                chunk_overlap=50
            )

            document_chunk_count += len(chunks)

            if chunks:

                print(
                    f"Page {page['page_number']}: "
                    f"{len(chunks)} chunks"
                )

        total_chunks += document_chunk_count

        print(
            "Total chunks for document:",
            document_chunk_count
        )

    print("\n")
    print("=" * 60)
    print(
        f"TOTAL CHUNKS: {total_chunks}"
    )
    print("=" * 60)


if __name__ == "__main__":

    main()
from app.config import DOCUMENT_FOLDER

from app.services.document_processor import (
    load_documents
)


def main():

    documents = load_documents(
        DOCUMENT_FOLDER
    )


    print("\n")
    print("=" * 60)
    print("DOCUMENT PROCESSING TEST")
    print("=" * 60)


    print(
        f"\nTotal documents: {len(documents)}"
    )


    for document in documents:

        print("\n")
        print(
            "Source:",
            document["source"]
        )

        print(
            "Pages:",
            len(document["pages"])
        )


        first_page = document["pages"][0]


        print(
            "\nFirst page preview:"
        )

        print(
            first_page["text"][:500]
        )


if __name__ == "__main__":

    main()
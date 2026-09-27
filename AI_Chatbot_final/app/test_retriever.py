from app.services.retriever import Retriever


def main():

    print("\n")
    print("=" * 70)
    print("SEMANTIC + KEYWORD SEARCH TEST")
    print("=" * 70)

    retriever = Retriever()

    while True:

        question = input(
            "\nAsk a question "
            "(type 'exit' to stop): "
        )

        if question.lower() == "exit":
            break

        results = retriever.retrieve(
            question,
            top_k=3
        )

        print("\n")
        print("=" * 70)
        print("TOP RESULTS")
        print("=" * 70)

        for number, result in enumerate(
            results,
            start=1
        ):

            document = result["document"]

            print(
                f"\nRESULT {number}"
            )

            print(
                "-" * 70
            )

            print(
                f"Source: {document['source']}"
            )

            print(
                f"Page: {document['page']}"
            )

            print(
                f"Chunk: {document['chunk_id']}"
            )

            print(
                f"Category: {result['category']}"
            )

            print(
                f"Category Match: "
                f"{result['category_match']}"
            )

            print(
                f"Keyword Score: "
                f"{result['keyword_score']:.3f}"
            )

            print(
                f"Final Score: "
                f"{result['final_score']:.3f}"
            )

            print("\nTEXT:")

            print(
                document["text"]
            )


if __name__ == "__main__":

    main()
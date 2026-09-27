from app.services.rag import (
    RAGService
)


def main():

    print("\n")
    print("=" * 70)
    print("AI STUDENT SUPPORT CHATBOT")
    print("=" * 70)


    rag = RAGService()


    while True:

        question = input(
            "\nStudent: "
        )


        if question.lower() == "exit":

            print(
                "\nGoodbye!"
            )

            break


        if not question.strip():

            continue


        print(
            "\nThinking..."
        )


        try:

            result = rag.ask(
                question
            )


            print("\n")
            print("=" * 70)
            print("CHATBOT")
            print("=" * 70)

            print(
                "\n"
                + result["answer"]
            )


            print("\n")
            print("SOURCES")
            print("-" * 70)


            for source in result["sources"]:

                print(

                    f"- "
                    f"{source['source']} "
                    f"(Page "
                    f"{source['page']})"

                )


        except Exception as e:

            print(
                "\nERROR:",
                str(e)
            )


if __name__ == "__main__":

    main()
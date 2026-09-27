from app.services.retriever import Retriever
from app.services.llm import LLMService


class RAGService:

    def __init__(self):

        self.retriever = Retriever()
        self.llm = LLMService()



    def is_university_question(self, question):

        question = question.lower()

        university_keywords = [

            # University
            "itm",
            "university",
            "college",
            "campus",

            # Admission
            "admission",
            "application",
            "eligibility",

            # Courses
            "course",
            "courses",
            "btech",
            "b.tech",
            "bba",
            "mba",
            "mca",
            "bca",
            "bsc",
            "msc",
            "engineering",
            "nursing",
            "agriculture",

            # Fees
            "fee",
            "fees",
            "tuition",

            # Academic
            "semester",
            "exam",
            "examination",
            "timetable",
            "academic calendar",
            "result",
            "attendance",

            # University people
            "vice chancellor",
            "chancellor",
            "registrar",
            "dean",
            "director",
            "faculty",

            # Student
            "student",
            "students",
            "hostel",

            # University information
            "notice",
            "notices",
            "notification",
            "parakh",
            "registered students",
            "campus achiever",
            "student innovation"
        ]

        for keyword in university_keywords:

            if keyword in question:

                return True

        return False



    def ask(self, question):

        question = question.strip()

        if not question:

            return {
                "answer": "Please enter a question.",
                "sources": []
            }



        university_question = (
            self.is_university_question(
                question
            )
        )

        print(
            "\nQuestion:",
            question
        )

        print(
            "University question:",
            university_question
        )



        if not university_question:

            print(
                "Using general AI mode..."
            )

            answer = (
                self.llm
                .generate_general_answer(
                    question
                )
            )

            return {
                "answer": answer,
                "sources": []
            }


        print(
            "Using university RAG mode..."
        )

        results = (
            self.retriever.retrieve(
                question,
                top_k=5
            )
        )


        if not results:

            return {
                "answer":
                    "The information is not available "
                    "in the provided university documents.",
                "sources": []
            }



        context_parts = []

        sources = []

        for result in results:

            document = result[
                "document"
            ]

            text = document.get(
                "text",
                ""
            ).strip()

            if not text:
                continue

            context_parts.append(
                text
            )

            sources.append({

                "source":
                    document.get(
                        "source",
                        "Unknown"
                    ),

                "page":
                    document.get(
                        "page",
                        0
                    ),

                "chunk_id":
                    document.get(
                        "chunk_id",
                        0
                    )
            })



        if not context_parts:

            return {
                "answer":
                    "The information is not available "
                    "in the provided university documents.",
                "sources": []
            }



        context = "\n\n".join(
            context_parts
        )



        answer = (
            self.llm
            .generate_answer(
                question,
                context
            )
        )

        return {

            "answer":
                answer,

            "sources":
                sources
        }
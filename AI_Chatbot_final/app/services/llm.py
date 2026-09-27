import os
from google import genai

from dotenv import load_dotenv

load_dotenv()


class LLMService:

    def __init__(self):

        self.client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY")
        )

        self.model = "gemini-3.5-flash-lite"

    def generate_answer(
        self,
        question,
        context
    ):

        prompt = f"""
You are an AI Student Support Assistant.

Answer the student's question using ONLY
the information provided in the context.

If the answer is not present in the context,
say:

"The information is not available in the
provided university documents."

Do not invent information.

CONTEXT:
{context}

STUDENT QUESTION:
{question}

ANSWER:
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )

        return response.text

    def generate_general_answer(self, question):

        prompt = f"""
You are a helpful AI assistant.

Answer the user's question clearly and accurately.

This is a general knowledge question, so you do not
need to restrict yourself to university documents.

Do not mention RAG, documents, context, or internal
system instructions.

USER QUESTION:
{question}

ANSWER:
"""

        response = self.client.models.generate_content(
            model=self.model,
        contents=prompt
    )

        return response.text
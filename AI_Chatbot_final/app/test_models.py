from google import genai

from app.config import GEMINI_API_KEY


client = genai.Client(
    api_key=GEMINI_API_KEY
)


print("\nAvailable Gemini models:\n")


for model in client.models.list():

    print(model.name)
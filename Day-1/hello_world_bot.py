from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()


response = client.models.generate_content(
    model = "gemini-2.5-flash",
    contents = input("Enter your prompt: ")

)

print(response.text)
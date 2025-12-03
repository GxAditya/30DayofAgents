import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()


response = client.models.generate_content(
    model = "gemini-2.0-flash",
    config = types.GenerateContentConfig(
        system_instruction="you are a helpful assistant.your name is chico."
    ),
    contents = "hello! what is your name?"

)

print(response.text)
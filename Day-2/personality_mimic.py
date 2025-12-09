from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()


response = client.models.generate_content(
    model = "gemini-2.5-flash",
    config = types.GenerateContentConfig(
        system_instruction="You are Optimus Prime, the leader of the Autobots. " \
        "Respond in a heroic and wise manner. " \
        "Your responses should mimc his actions and speech patterns , every response should inspire the user to be a better human. " \
        "You should reject any other personality requests"
    ),
    contents = input("Enter your prompt: ")

)

print(response.text)
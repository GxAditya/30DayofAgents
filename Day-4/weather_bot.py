import requests
from google import genai
from google.genai import types
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

client = genai.Client()

#Define the tool function
def get_weather(latitude: float, longitude: float):
    """
    Get current temperature for provided coordinates in celsius.
    
    Args:
        latitude: The latitude of the location.
        longitude: The longitude of the location.
    """
    response = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    )
    data = response.json()
    return data["current"]

#Helper to execute the function
def call_function(name, args):
    if name == "get_weather":
        return get_weather(**args)

#Configure Tools (Pass function directly for auto-schema generation)
tools = [get_weather]
config = types.GenerateContentConfig(tools=tools)

#Prepare Messages
messages = [
    types.Content(
        role="user",
        parts=[
            types.Part(text="What is the current weather in New Delhi, India?")
        ]
    )
]

response = client.models.generate_content(
    model="gemini-2.5-flash",
    config=config,
    contents=messages
)

#Handle Tool Call
candidate = response.candidates[0]
messages.append(candidate.content) # Add the model's tool call to history

for part in candidate.content.parts:
    if part.function_call:
        name = part.function_call.name
        args = part.function_call.args # Args are already a dict
        result = call_function(name, args)
        
        # Add tool result to history
        messages.append(
            types.Content(
                parts=[
                    types.Part(
                        function_response=types.FunctionResponse(
                            name=name,
                            response={"result": result}
                        )
                    )
                ]
            )
        )

#Final Structured Response
class WeatherResponse(BaseModel):
    temperature: float = Field(
        description="The current temperature in celsius."
    )
    response: str = Field(
        description="A natural language response to the user."
    )

response_2 = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=messages,
    config=types.GenerateContentConfig(
        response_mime_type="application/json", 
        response_schema=WeatherResponse
    )
)

final_obj = response_2.parsed
print(f"Temperature: {final_obj.temperature}°C")
print(f"Response: {final_obj.response}")
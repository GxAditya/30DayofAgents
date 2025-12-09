import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

client = genai.Client()



def search_kb(question: str):
    """
    Load the whole knowledge base from the txt file and search for the answer.
    
    Args:
        question: The question to search for.
    (This is a mock function for demonstration purposes, we don't search)
    """
    file_path = os.path.join(os.path.dirname(__file__), "biodata.txt")
    with open(file_path, "r") as f:
        return f.read()
    
def call_function(name, args):
    if name == "search_kb":
        return search_kb(**args)    
    
tool= types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="search_kb",
            description="Load the whole knowledge base from the txt file and search for the answer.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "question": types.Schema(type=types.Type.STRING),
                },
                required=["question"],
            ),
        ),
    ],
)
config = types.GenerateContentConfig(tools=[tool])

messages = [
    types.Content(
        role="user",
        parts=[
            types.Part(text="What information do you have about Aditya Kumar?")
        ]
    )
]

response = client.models.generate_content(
    model="gemini-2.5-flash",
    config=config,
    contents=messages
)

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

class SearchResponse(BaseModel):
    answer: str = Field(
        description="The answer to the question."
    )
    response: str = Field(
        description="A natural language response to the user."
    )

response_2 = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=messages,
    config=types.GenerateContentConfig(
        response_mime_type="application/json", 
        response_schema=SearchResponse
    )
)

final_obj = response_2.parsed
print(f"Answer: {final_obj.answer}")
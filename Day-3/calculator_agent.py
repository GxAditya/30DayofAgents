from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()


def calculate(expression):
    try:
        return eval(expression)
    except:
        return "Error in calculation"

calculate_declaration = {
    "name": "calculate",
    "description": "Evaluates a mathematical expression.",
    "parameters": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "The mathematical expression to evaluate."
            }
        },
        "required": ["expression"]
    }
}

tools = types.Tool(function_declarations=[calculate_declaration])
config = types.GenerateContentConfig(tools=[tools])

response = client.models.generate_content(
    model = "gemini-2.5-flash",
    config = config,
    contents = "Calculate the result of 15 * 3 + 2"

)

print(response.text)

if response.candidates[0].content.parts[0].function_call:
    function_call = response.candidates[0].content.parts[0].function_call
    print(f"Function to call: {function_call.name}")
    print(f"Arguments: {function_call.args}")
    result = calculate(**function_call.args)
    print(f"Calculation result: {result}")
else:
    print("No function call found in the response.")
    print(response.text)
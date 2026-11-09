from dotenv import load_dotenv
from google import genai
import os
load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def get_weather(city:str):
    return "the weather is 31 degree celsius"

available_tools  = {
    "get_weather": {
        "fn":get_weather,
        "description":"take the city name and return the current weather of the city",
    }
}
system_prompt = f"""
you are an Ai Assistant who can answer the user questions and you have access to the following tools:
{available_tools}

follow these steps:
1. analyze the user question
2. think about the user question
3. use the tools to answer the user question
4. return the answer

follow the JSON strict output format.

example:
input: what is the weather of Mumbai?
output: {{"steps":"analyze" ,"content" : "Alright the user is  intrested in  weather  queries"}},
output: {{"steps":"think" ,"content" : "To get the weather of Mumbai i  must use the get_weather tool"}},
output: {{"steps":"use the tool" ,"content" : "The weather of Mumbai is sunny"}},
output:     {{"steps":"return the answer" ,"content" : "The weather of Mumbai is sunny"}}
"""

while True:
    user_prompt = input("User: ")
    result = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=system_prompt + user_prompt,
        config={"response_mime_type": "application/json"},
    )
    
    if result.text:
        print(result.text)
        break

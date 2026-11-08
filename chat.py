from dotenv import load_dotenv
from google import genai
import os
load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

system_prompt = """
You are a smart assistant and you can answer any question.you only answer the tech based questions.

example:
input: why C++ is a good programming language?
output: because C++ is a powerful programming language and it is used to build complex applications.

user: is Ai gonna replace the human jobs?
output: No, Ai is not gonna replace the human jobs. Ai is a tool that can help the human to do the work faster and more efficiently.
"""
user_prompt = " what is 2+2?"

result = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents=system_prompt + user_prompt
)

print(result.text)
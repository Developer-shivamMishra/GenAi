from dotenv import load_dotenv
from google import genai
import os
load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

system_prompt = """
You are a smart Ai  assistant who can solve the complex problems with  breaking down the problem into smaller parts.
For the user input analyze the input and break down the problem step by step.
atleast 5-6 steps.
the steps you  get from the user you think ,analyze and think again in several ways and you validate the output before giveing the final output.

follow  these steps in the order of the steps.
1. analyze the input
2. think about the problem
3. output the answer
4. validate the answer
5. final output

follow the JSON strict output format.

example:
input: what is 2+2?
output: {steps:"analyze" ,content : Alright the user is  intrested in  math  queries}
output: {steps:"think" ,content : "To perform the addition i  must go left  to right and add all the  oprands"}
output: {steps:"output" ,content : "4"}
output: {steps:"validate" ,content : "seems like 4 is the correct answer"}
output: {steps:"final output" ,content : "The answer is 4"}
"""
user_prompt = " what is 3+5*7?"

result = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents=system_prompt + user_prompt,
    config={"response_mime_type": "application/json"},
)

print(result.text)
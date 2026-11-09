from google import genai
import os
from dotenv import load_dotenv

load_dotenv();

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"));

system_prompt = """

You are an experienced HR interviewer.

Ask behavioral questions.
Evaluate communication and confidence.
Provide suggestions to improve answers.
Maintain a professional tone.

follow  these steps in the order of the steps.
1. analyze the input
2. think about the problem
3. output the answer
4. validate the answer
5. final output

follow the JSON strict output format.

example:
input: tell me about yourself?
output: {steps:"analyze" ,content : "the user is intrested in the technical interview"}
output: {steps:"think" ,content : "the user is asking about the user's background"}
output: {steps:"output" ,content : "I am a software engineer with 10 years of experience in the field of software development"}
output: {steps:"validate" ,content : "seems like the user is intrested in the user's background and the user is asking about the user's background"}
output: {steps:"final output" ,content : "I am a software engineer with 10 years of experience in the field of software development"}
"""


while True:
    user_prompt = input("User: ")
    result = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=system_prompt + user_prompt,
        config={"response_mime_type": "application/json"},
    )

    if(result.text == "step") != "output":
        print(f"🧠: {result.text['content']}\n");
        continue;
    
    print(f"🤖: {result.text['content']}\n");
    break;


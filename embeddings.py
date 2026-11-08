from dotenv  import load_dotenv;
from openai import OpenAi;

load_dotenv();

client  = OpenAi();

text= "Eiffel tower is in paris and it  is  famous  landmark";

response = client.embeddings.create(

    input = text;
    model = "text-embedding-3-small"
)

print("vector embeddings" , response.data[0].embedding)
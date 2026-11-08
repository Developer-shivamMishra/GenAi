import tiktoken

encoder = tiktoken.encoding_for_model("gpt-4o")

print("vocabSize" ,  encoder.n_vocab);

text = "cats are cars";

print(encoder.encode(text))
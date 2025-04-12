print('hello world!!')

import tiktoken 


encoder = tiktoken.encoding_for_model("gpt-4o");

print(encoder.n_vocab) # 200k 
# this are the number of token available in the model

text = "hello world !"
print(encoder.encode(text))

print(encoder.decode([24912, 2375, 0, 2])) # hello world !

# so yaha ho ye rha hai ki har text , number ya to special character ka ek token and from all the combination possible with this are coverd in the vocab of this model and it encodes and decodes as well. 


import tokenizers as tk

data = tk.Encoder()

print(data.encoder("hello there everyone"))
print(data.decoder([104101108108111, 116104101114101, 101118101114121111110101]))

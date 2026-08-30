import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import joblib
import requests
from config import api_key

def create_embedding(text_list):

    r = requests.post(
        "http://localhost:11434/api/embed",
        json={
            "model": "bge-m3",
            "input": text_list,
            
        }
    )
    
    print("STATUS:",r.status_code)
    embedding = r.json()["embeddings"]
    return embedding
 
def inference(prompt):
    r = requests.post(
            "http://localhost:11434/api/generate",
            json={
                # "model":"deepseek-r1",
                "model":"llama3.2",
                "prompt": prompt,
                "stream": False
                })
    response = r.json()
    print(response)
    return response

df = joblib.load('embeddings.joblib')


incoming_query = input("Ask a Question: ")
question_embedding = create_embedding([incoming_query])[0]

similarities = cosine_similarity(np.vstack(df['embedding']),[question_embedding]).flatten()
# print(similarities)
top_results = 3
max_ind = similarities.argsort()[::-1][0:top_results] 
new_df = df.loc[max_ind]

prompt = f'''I am teaching web development in my Sigma web development course. Here are video subtitle chunks containing video title, video number, start time in seconds, end time in seconds, the text at that time:

{new_df[["title", "number", "start", "end", "text"]].to_json(orient="records")}
---------------------------------
"{incoming_query}"
User asked this question related to the video chunks, you have to answer in a human way (dont mention the above format, its just for you) where and how much content is taught in which video (in which video and at what timestamp) and guide the user to go to that particular video. If user asks unrelated question, tell him that you can only answer questions related to the course
'''

with open("prompt.txt","w") as f:
    f.write(prompt)

response = inference(prompt)["response"]
print(response)

with open("response.txt","w") as f:
    f.write(response)


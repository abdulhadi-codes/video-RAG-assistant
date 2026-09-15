from sklearn.metrics.pairwise import cosine_similarity
import joblib
import numpy as np
import pandas as pd
import requests

def create_embedding(text_list):

    r = requests.post(
        "http://localhost:11434/api/embed",
        json={
            "model": "bge-m3",
            "input": text_list
        }
    )
    embeddings = r.json("embeddings")
    return embeddings

df = joblib.load('embeddings.joblib')

incoming_query = input("Ask Question: ")
embeddings = create_embedding([incoming_query])[0]
# print(embeddings)

# Find Similarities of embeddings with other embeddings

# print(np.vstack(df['embedding'].values))
# print(np.vstack(df['embedding'].shape))

similarites = cosine_similarity(np.vstack(df['embedding']),[embeddings]).flatten()
print(similarites)
top_results = 3 
max_indx = similarites.argsort()[-3::-1][0:top_results]
print(max_indx)
new_df = df.loc[max_indx]
print(new_df[["title","number","text"]])



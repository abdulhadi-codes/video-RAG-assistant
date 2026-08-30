import requests
import os
import json
import pandas as pd
import joblib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def create_embedding(text_list):

    r = requests.post(
        "http://localhost:11434/api/embed",
        json={
            "model": "bge-m3",
            "input": text_list
        }
    )
    print("STATUS:", r.status_code)
    data = r.json()

    if "embeddings" not in data:  
        print("\nERROR RESPONSE:")
        print(data)
        print("Length of text_list:", len(text_list))
        raise Exception("No embeddings key found")
    return data["embeddings"]

jsons = os.listdir("json")

my_dicts = []
chunk_id = 0
batch_size = 20

for json_file in jsons:
    with open(f"json/{json_file}") as f:
        content = json.load(f)

    print(f"\nCreating embeddings for {json_file}")
    total_chunks = len(content["chunks"])
    print("Total Chunks:", total_chunks)

    for start in range(0, total_chunks, batch_size):
        batch = content["chunks"][start:start + batch_size]
        print(f"Creating embeddings for chunks "
            f"{start} to {start + len(batch) - 1}")
        texts = [c["text"] for c in batch]
        embeddings = create_embedding(texts)

        for i, chunk in enumerate(batch):
            chunk["chunk_id"] = chunk_id
            chunk["embedding"] = embeddings[i]
            chunk_id += 1
            my_dicts.append(chunk)
            # print(f"Finished batch {start} to {start + len(batch) - 1}")
           

# print("Total Chunks Processed:", len(my_dicts))
df = pd.DataFrame.from_records(my_dicts)
# save this DataFrame
joblib.dump(df, "embeddings.joblib")
# print(df)
incoming_query = input("Ask Question: ")
question_embedding = create_embedding([incoming_query])[0]
# print(question_embedding)

# Find Similarities of question_embedding with other embeddings

# print(np.vstack(df['embedding'].values))
# print(np.vstack(df['embedding'].shape))

similarites = cosine_similarity(np.vstack(df['embedding']),[question_embedding]).flatten()
print(similarites)
top_results = 3 
max_indx = similarites.argsort()[-3::-1][0:top_results]
print(max_indx)
new_df = df.loc[max_indx]
print(new_df[["title","number","text"]])



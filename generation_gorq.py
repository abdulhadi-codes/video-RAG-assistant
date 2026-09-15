import time
import requests
import joblib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from groq import Groq
from config import api_key

df = joblib.load("embeddings.joblib")
groq_client = Groq(api_key=api_key)

top_k = 3


def create_embedding(text_list):
    r = requests.post(
        "http://localhost:11434/api/embed",
        json={"model": "bge-m3", "input": text_list}
    )

    data = r.json()
    if "embeddings" not in data:
        raise RuntimeError(f"Ollama embedding failed: {data}")
    return data["embeddings"]

# retrieval of Top3 Chunks

def retrieve_top_chunks(question_embedding, k=top_k):
    similarities = cosine_similarity(
        np.vstack(df["embedding"]),
        [question_embedding]
    ).flatten()
    top_indices = similarities.argsort()[::-1][:k]
    return df.iloc[top_indices]

def format_time(seconds) -> str:
    total_seconds = round(seconds)
    mins, secs = divmod(total_seconds, 60)
    return f"{mins}:{secs:02d}"


def build_context_string(chunks) -> str:
    blocks = []
    for _, row in chunks.iterrows():
        blocks.append(
            f"Video {row['number']} - {row['title']} "
            f"[{format_time(row['start'])} - {format_time(row['end'])}]\n{row['text']}"
        )
    return "\n\n".join(blocks)


def build_prompt(question: str, context: str) -> str:
    return (
        "You are answering questions about a course based only on the "
        "video transcript excerpts below. Cite the video number and "
        "timestamp in your answer.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        "Answer:"
    )


def generate_answer(prompt: str) -> str:
    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=500,
    )
    return response.choices[0].message.content


def answer_question(question: str):
    """Full pipeline: question -> embedding -> retrieval -> prompt -> answer.
    Returns everything the frontend's response card needs, with a real
    measured response_time — nothing fabricated."""
    start = time.perf_counter()

    q_embedding = np.array(create_embedding([question])[0])
    top_chunks = retrieve_top_chunks(q_embedding)
    context = build_context_string(top_chunks)
    prompt = build_prompt(question, context)
    answer = generate_answer(prompt)

    elapsed_ms = round((time.perf_counter() - start) * 1000)

    sources = [
        {
            "video_number": row["number"],
            "video_title": row["title"],
            "start": row["start"],
            "end": row["end"],
        }
        for _, row in top_chunks.iterrows()
    ]

    return {
        "answer": answer,
        "context": context,
        "sources": sources,
        "response_time": f"{elapsed_ms}ms",
    }   

# def print_sources(sources):
#     print(f"Response time: {result['response_time']}")
#     for s in sources:
#         print(f"- Video {s['video_number']} · {format_time(s['start'])}–{format_time(s['end'])}")


# if __name__ == "__main__":
#     result = answer_question("What is the AutoPlay attribute?")
#     print(result["answer"])
#     print()
#     print_sources(result["sources"])

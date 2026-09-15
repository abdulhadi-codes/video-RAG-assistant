# How to use this RAG AI Teaching assistant on your own data

## Step 1 - Collect your Videos
Move all your video files to the other videos 

## Step 2 - Convert to mp3
Convert all the video files to mp3 by running video_to_mp3(Process_video.py)

## Step 3 - Convert mp3 to json
Convert all the mp3 files to json by running mp3_to_json(speech_to_text.py)

## Step 4 - Convert the json files to Vectors
Use the file preprocess_json to convert the json file to dataframe with Embeddings and save it as joblib pickle

## Step 5 - Prompt generation and feeding to LLM 

Read the joblib file and load it into the memory. Then create a relevent prompt as per the user query and feed it to the LLM    

# Video RAG Assistant

A Retrieval-Augmented Generation system that transcribes course lecture videos and answers natural-language questions with cited source video and timestamp — turning hours of lecture footage into a searchable knowledge base instead of something you scrub through manually.

## Checkout the SCREEN_SHOTS folder for .png images and its working 
---

## Overview

Finding a specific concept inside a long series of lecture videos usually means scrubbing through a timeline by hand, guessing where something was explained. This project solves that by transcribing every video, breaking the transcripts into searchable chunks, embedding them, and retrieving the most relevant passages for any question a user asks — then generating a direct answer via an LLM, with the exact video and timestamp cited alongside it.

The system currently runs against a set of indexed course lecture videos and answers questions entirely from that transcript content — it does not answer from general knowledge outside the indexed videos.

---

## Key Features

- Video-to-audio extraction and speech-to-text transcription
- Timestamped transcript chunking
- Vector embedding generation for semantic (meaning-based) search
- Cosine-similarity based retrieval of the most relevant transcript chunks
- LLM-based answer generation grounded in retrieved context
- Source video number and timestamp citation on every answer
- Flask backend with a REST-style `/query` endpoint
- Web interface for asking questions and viewing responses
- Modular pipeline design — each pipeline stage lives in its own module
- Swappable LLM backend (hosted API vs. local inference)

---

## How It Works


Course Video
     ↓
Audio Extraction (FFmpeg)
     ↓
Speech-to-Text Transcription (Whisper)
     ↓
Timestamped Chunking
     ↓
Embedding Generation (BGE-M3)
     ↓
Vector Storage (Pandas DataFrame + Joblib)
     ↓
Question → Question Embedding
     ↓
Cosine Similarity Retrieval (Top-K chunks)
     ↓
Context-Grounded Prompt Construction
     ↓
LLM Answer Generation
     ↓
Answer + Source Video + Timestamp


---

## System Architecture


Frontend (HTML / CSS / JavaScript)
        ↓
Flask API (app.py)
        ↓
RAG Pipeline 
     │── speech_to_text.py, process_video.py        # FFmpeg audio extraction + Whisper transcription
     │── create_chunks.py                           # Builds timestamped transcript chunks
     │── process_incoming.py                        # Embedding generation (indexing + query time)
     │── read_chunks.py                             # Loads/saves the embedded dataset via Joblib
     │── generation_groq.py                         # Cosine similarity top-K chunk retrieval
     │── generation_groq.py                         # Prompt construction + LLM answer generation

Embeddings: BGE-M3 served locally through Ollama's embedding API.

---

## Technology Stack

| Component | Technology | Purpose |

| Language | Python | Core application and pipeline |

| Backend | Flask | API layer and application server |

| Transcription | OpenAI Whisper | Speech-to-text on lecture audio |

| Audio extraction | FFmpeg | Extracting audio from video files |

| Embeddings | BGE-M3 | Vector representations of transcript chunks |

| Retrieval | scikit-learn (cosine similarity) | Ranking chunks by relevance to a question |

| Storage | Pandas + Joblib | Persisting the embedded chunk dataset |

| LLM generation | Groq-hosted chat model (with a local Ollama-based alternative) | Generating the final natural-language answer |
| Frontend | HTML, CSS, JavaScript | Chat interface and response display |

> **Note:** the embedding step and the LLM generation step each support more than one backend in this repository — a locally-running option (Ollama) alongside a hosted-API option (BGE-M3 for embeddings, Groq for generation). Confirm in `read_chunks.py` and `generation_groq.py` which is currently wired into `app.py` in your deployed version.

---

## Project Structure

Video-RAG-Assistant/
│
├── app.py                     # Flask entry point — routes and request handling
├── config.py                  # Add your Local API key 
│
|
│── speech_to_text.py, process_video.py        # FFmpeg audio extraction + Whisper transcription
│── create_chunks.py                           # Builds timestamped transcript chunks
│── process_incoming.py                        # Embedding generation (indexing + query time)
│── read_chunks.py                             # Loads/saves the embedded dataset via Joblib
│── generation_groq.py                         # Cosine similarity top-K chunk retrieval
│── generation_groq.py                         # Prompt construction + LLM answer generation
│
├── templates/
│   └── index.html             # Web interface
│
├── static/
│   ├── style.css               # Interface styling
│   └── script.js               # Frontend logic — calls /query, renders responses
│
├── requirements.txt           # Python dependencies
├── .gitignore                 # Excludes config.py, embeddings data, raw media
├── .env.example               # Documents required environment variables 
└── README.md


---

## RAG Pipeline Explanation

**Ingestion**
Course videos are processed offline, ahead of time,this is a one-time indexing step, separate from answering live queries.

**Transcription**
Audio is extracted from each video with FFmpeg, then transcribed with OpenAI Whisper, producing timestamped segments of text.

**Chunking**
Whisper's segments are organized into chunks, each tagged with its source video number/title and start/end timestamp, so retrieval results can always be traced back to an exact moment in a specific video.

**Embeddings**
Each chunk's text is embedded using the BGE-M3 model, converting it into a vector representation suitable for similarity search. The same embedding step is reused at query time to embed the user's question into the same vector space.

**Retrieval**
A user's question is embedded, then compared against every stored chunk embedding using cosine similarity. The top-K most similar chunks are selected as context for the answer.

**Generation**
The retrieved chunks are assembled into a grounded prompt — including their video number and timestamps — and passed to an LLM, which is instructed to answer only from that context and to cite the relevant timestamp.

**Response**
The Flask backend returns the generated answer, the source chunks used, and a measured response time as JSON, which the frontend renders as a chat-style response card.

---

## Installation
Install the external dependency: Ollama

ollama pull bge-m3
Then verify it  -> ollama list

You will see something similar to: bge-m3

git clone https://github.com/abdulhadi-codes/video-rag-assistant.git

cd video-rag-assistant

pip install -r requirements.txt


---

## Environment Variables

Create a `config.py` file locally (excluded from git via `.gitignore`) containing your API key:

api_key = "your_api_key_here"

See `.env.example` for the required variable shape:


GROQ_API_KEY=your_api_key

A Groq API key can be obtained from [console.groq.com](https://console.groq.com).

---

## Running the Application

```bash
python app.py
```


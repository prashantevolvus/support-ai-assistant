from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer
import openai
import os

# Initialize FastAPI app
app = FastAPI()

# Configure CORS to allow the frontend to communicate with this backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables or set defaults.
openai.api_key = os.environ.get("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY")

# Instantiate the embedding model and FAISS index.
embedder = SentenceTransformer("all-MiniLM-L6-v2")
# The dimension of the MiniLM model embeddings is 384.
index = faiss.IndexFlatL2(384)
knowledge_base = []

class Query(BaseModel):
    """Schema for incoming chat queries."""
    question: str


@app.post("/upload/")
async def upload_file(file: UploadFile):
    """
    Upload a CSV file containing past issues and resolutions.
    Each row should have 'issue' and 'resolution' columns.
    The text from both columns is concatenated, embedded,
    and added to the vector search index.
    """
    df = pd.read_csv(file.file)
    count = 0
    for _, row in df.iterrows():
        # Compose a single text entry from issue and resolution.
        text = f"Issue: {row['issue']} | Resolution: {row['resolution']}"
        emb = embedder.encode([text])
        index.add(emb)
        knowledge_base.append(text)
        count += 1
    return {"status": f"Uploaded and indexed {count} entries"}


@app.post("/chat/")
async def chat(query: Query):
    """
    Respond to a user question using retrieval-augmented generation.
    A query is embedded, similar knowledge entries are retrieved,
    and the context is passed to an LLM to generate an answer.
    """
    q_emb = embedder.encode([query.question])
    k = 3
    D, I = index.search(q_emb, k)
    # Guard against indices that may be out of range if less than k entries exist.
    retrieved = [knowledge_base[i] for i in I[0] if i < len(knowledge_base)]

    # Construct prompt for the LLM, including retrieved context.
    prompt = (
        "You are a helpful support assistant. "
        "Use the following context from previous issues and resolutions to answer "
        "the user's question.\n\n"
        f"Context: {retrieved}\n\n"
        f"Question: {query.question}\n"
        "Answer:"
    )

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful support assistant."},
            {"role": "user", "content": prompt},
        ],
    )
    answer = response["choices"][0]["message"]["content"]
    return {"answer": answer, "sources": retrieved}

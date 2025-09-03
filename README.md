# Support AI Assistant

This repository contains a simple prototype of a React + Python application that demonstrates how to build a support assistant powered by retrieval‑augmented generation (RAG). The system allows support teams to upload historical FAQ and ticket data, embed it for semantic search, and chat with an assistant that uses prior resolutions to answer questions.

## Features

- **Upload FAQ and ticket history** as CSV files with `issue` and `resolution` columns.
- **Backend API** built with FastAPI; it embeds the uploaded data using SentenceTransformers, stores them in an in‑memory FAISS index, and uses the OpenAI API for generating responses.
- **React Frontend** that provides a user interface for uploading data and chatting with the assistant.
- **Continuous learning** can be enabled by logging user questions and answers for later fine‑tuning or re‑embedding.

## Getting Started

1. Install dependencies for the backend:

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. Start the backend API:

   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

3. Install dependencies and run the frontend:

   ```bash
   cd ../frontend
   npm install
   npm start
   ```

4. Upload a CSV file with columns `issue` and `resolution`.

5. Ask questions in the chat interface and get responses based on your historical data.

## Deployment

For local development, you can run the backend and frontend separately. If you prefer Docker, a basic `docker-compose.yml` is provided:

```yaml
version: "3.8"
services:
  backend:
    build:
      context: ./backend
    ports:
      - "8000:8000"
  frontend:
    build:
      context: ./frontend
    ports:
      - "3000:3000"
    stdin_open: true
    tty: true
```

This will build and run both services. Note that the Docker configuration is minimal and may need adjustments depending on your environment.

## Notes

- Set your `OPENAI_API_KEY` environment variable before running the backend to use the OpenAI API.
- For production use, consider replacing the in‑memory FAISS index with a persistent vector database (e.g., Pinecone, Weaviate, or pgvector).
- This is a simple prototype intended for educational purposes and may require additional security and performance considerations for real‑world deployment.

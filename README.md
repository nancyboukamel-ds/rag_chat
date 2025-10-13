# RAG Voice App — Document Management & Chatbot System

This project is a **Retrieval-Augmented Generation (RAG)**-powered chatbot built with **LangChain**, **Google Gemini**, **ChromaDB**, and **FastAPI**, combined with a **Streamlit frontend** for document management and chat interactions.

---

## Features

### Document Management

* Upload, list, and delete documents.
* Each document is stored in:

  * **MongoDB** (metadata)
  * **ChromaDB** (vector embeddings for retrieval)
* Integrated backend API to sync between both stores.

### RAG Chatbot

* Powered by **Gemini (via `ChatGoogleGenerativeAI`)**.
* Combines user queries with context retrieved from your uploaded documents.
* Optionally supports **chat history awareness** (via `create_history_aware_retriever`).

### File List Management (Streamlit)

* Displays all uploaded files with metadata (filename, upload date).
* Includes **Delete button** for each document.
* Automatically refreshes the file list after deletion.

---

## Project Structure

```
rag_voice/
├── backend/
│   ├── api.py                # FastAPI app
│   ├── langchain_utils.py    # LLM & RAG chain setup
│   ├── chroma_utils.py       # Vectorstore setup and management
│   ├── db_utils.py           # MongoDB connection helpers
│   └── models.py             # Pydantic request/response models
│
├── frontend/
│   └── app.py                # Streamlit UI (chat + document manager)
│
├── .env                      # Environment variables
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

---

## Setup Instructions

### Clone the repository

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
```

### Create and activate a virtual environment

```bash
python3 -m venv rag_voice
source rag_voice/bin/activate  # On Windows: rag_voice\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Add environment variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_google_api_key
RETRIEVER_K=4
LLM_TEMPERATURE=0.7
MONGO_URI=mongodb://localhost:27017
DB_NAME=rag_voice_db
```

---

## 🖥️ Running the App

### Start the FastAPI backend

```bash
cd backend
uvicorn api:app --reload
```

Backend will run on: `http://127.0.0.1:8000`

---

### Start the Streamlit frontend

```bash
cd frontend
streamlit run app.py
```

Frontend will run on: `http://localhost:8501`


---

## 🧠 RAG Architecture Overview

```
User Query ─┬──────────────┐
             │              ▼
     Chat History     create_history_aware_retriever
             │              ▼
             ├──────────> Retriever ─────┐
             │                           ▼
             └──────→ create_stuff_documents_chain
                             │
                             ▼
                      Gemini LLM (QA Chain)
                             │
                             ▼
                        AI Response
```

---

## API Endpoints

| Method | Endpoint      | Description                     |
| -----: | ------------- | ------------------------------- |
|  `GET` | `/list-docs`  | List all uploaded documents     |
| `POST` | `/delete-doc` | Delete a document by ID         |
| `POST` | `/chat`       | Send a query to the RAG chatbot |

---

## Contributing

1. Fork the repo
2. Create a new branch (`feature/my-feature`)
3. Commit your changes
4. Push and open a PR 

---

## Tech Stack

* **Frontend:** Streamlit
* **Backend:** FastAPI
* **LLM:** Google Gemini (via LangChain)
* **Database:** MongoDB
* **Vector Store:** ChromaDB
* **Language:** Python 3.10+

Would you like me to include a short **“delete flow diagram”** in Markdown (showing what happens when you click delete)? It makes the README even clearer for contributors.

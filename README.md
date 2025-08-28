# GitLab Handbook RAG AI Chatbot

This project is a Retrieval-Augmented Generation (RAG) based chatbot designed to answer questions about the GitLab Handbook. It uses a sophisticated pipeline to ingest, process, and index content from the handbook, providing accurate, context-aware answers with citations.

## Core Functionality

- **Web Crawling & Ingestion**: Automatically crawls the GitLab Handbook and direction pages to gather the latest information.
- **Content Processing**: Extracts the main content from web pages, converts it to clean Markdown, and splits it into manageable chunks.
- **Vector Embeddings**: Generates dense vector embeddings for each content chunk using state-of-the-art models.
- **Vector Storage**: Stores and indexes the embeddings in a specialized vector database for efficient similarity searches.
- **Retrieval-Augmented Generation (RAG)**:
    - When a user asks a question, the system retrieves the most relevant document chunks from the vector database.
    - It uses the user's query and chat history to rewrite a better search query.
    - The retrieved context is then passed to a powerful Large Language Model (LLM) to generate a comprehensive answer.
- **Citations**: Provides citations from the source documents, allowing users to verify the information and explore topics in more detail.
- **Interactive UI**: A user-friendly, secure web interface for interacting with the chatbot.

## Tech Stack

| Component | Technology | Description |
| --- | --- | --- |
| **Backend** | Python, FastAPI | High-performance asynchronous API for serving the chat and ingestion logic. |
| **Frontend** | Streamlit | Interactive and easy-to-use web interface for the chatbot. |
| **Vector DB** | Qdrant | Efficient storage and retrieval of vector embeddings. |
| **LLM** | Gemini 1.5 Flash | State-of-the-art language model for generating answers. |
| **Embeddings** | BAAI/bge-m3 | High-quality sentence embedding model. |
| **Ingestion** | trafilatura, markdownify | Tools for extracting main content from HTML and converting it to Markdown. |
| **Chunking** | LangChain | Library used for splitting text into semantic chunks. |

## Technical Approach

### 1. Data Ingestion and Processing

The ingestion pipeline is the foundation of the RAG system.

- **Crawling**: A recursive crawler starts from a set of base URLs (`https://handbook.gitlab.com/`, `https://about.gitlab.com/direction/`) and discovers new pages. It uses a `user-agent` and respects a maximum page and depth limit to be a responsible scraper.
- **Content Extraction**: For each crawled URL, `trafilatura` is used to extract the core article content, filtering out boilerplate like headers, footers, and ads.
- **HTML to Markdown**: The extracted HTML is converted to Markdown using `markdownify`. This simplifies the text, removes complex styling, and prepares it for clean chunking.

### 2. Chunking and Embedding

- **Chunking**: The clean Markdown content is split into smaller, overlapping chunks using `langchain-text-splitter`. The `chunk_size` of 800 characters with a `chunk_overlap` of 200 ensures that semantic context is preserved at the boundaries of chunks.
- **Embedding**: Each chunk is then converted into a numerical representation (embedding) using the `BAAI/bge-m3` model. This model is chosen for its excellent performance in capturing semantic meaning, which is crucial for effective retrieval.

### 3. Storage and Retrieval

- **Vector Database**: The generated embeddings and their corresponding text chunks are stored in a `Qdrant` collection. Qdrant is a highly efficient vector database optimized for fast similarity searches.
- **Retrieval**: When a user asks a question, the query is embedded using the same `bge-m3` model. The system then searches Qdrant for the `k` most similar document chunks based on cosine similarity.

### 4. Generation and Citation

- **Query Enhancement**: The system leverages the chat history to understand the context of the conversation. It uses the LLM to rewrite the user's latest query into a more descriptive and context-aware question, leading to better retrieval results.
- **Context-Aware Generation**: The retrieved document chunks are combined with the rewritten query and a system prompt, and then passed to the `Gemini 1.5 Flash` model. The LLM generates a human-like answer based *only* on the provided context.
- **Citation Analysis**: After generating the answer, the system analyzes it to identify which parts of the response correspond to which source documents. It then presents these sources as citations, providing transparency and allowing for further reading.

## Demo Video 

[![Demo Video](https://img.youtube.com/vi/6f86eFwac14/0.jpg)](https://www.youtube.com/watch?v=6f86eFwac14)

## Local Setup and Running

Follow these instructions to set up and run the chatbot on your local machine.

### Prerequisites

- **Python 3.9+**
- **Docker** and **Docker Compose**
- **Git**
- **Gemini API Key**: Get one from [Google AI Studio](https://aistudio.google.com/app/apikey).

### 1. Clone the Repository

```bash
git clone https://github.com/mayank-sheoran/gitlab-handbook-rag-ai.git
cd gitlab-handbook-rag-ai
```

### 2. Environment Variables

Update `.env` file in the root of the project with your_gemini_api_key:

```env
GEMINI_API_KEY=your_gemini_api_key
BACKEND_URL=http://host.docker.internal:9999
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

### 3. Run the Application with Docker Compose

This is the recommended way to run the application.

**Step 1: Build and Start Services**

```bash
docker-compose up --build
```

Recommended: run backend separately on localhost as GPU is required for embedding model
```bash
uvicorn app.main:app --host 0.0.0.0 --port 9999
```

This command will:
- Build the Docker image for the application.
- Start the Qdrant, backend, and frontend service.
- The services will be available at:
  - **Backend**: `http://localhost:9999`
  - **Frontend**: `http://localhost:9998`
  - **Qdrant UI**: `http://localhost:6334/dashboard`
  - **Qdrant API**: `http://localhost:6333`


**Step 2: Run the Ingestion Process**

Once the services are running, populate the vector database by sending a POST request to the `/ingest` endpoint. Open a new terminal for this.

```bash
curl -X POST http://localhost:9999/ingest
```
This process will take some time as it crawls, processes, and embeds the handbook content. You can monitor the progress in the Docker Compose logs.

**Step 3: Access the Chatbot**

Navigate to `http://localhost:9998` in your browser. 


## Project Structure

```
.
├── app/                  # Backend FastAPI application
│   ├── main.py           # FastAPI app entrypoint
│   ├── api/              # API routers (chat, ingest, health)
│   ├── domain/           # Core business logic and data models
│   ├── services/         # Services for chat, ingestion, embedding, etc.
│   └── utils/            # Utility functions
├── streamlit_app.py      # Frontend Streamlit application
├── requirements.txt      # Python dependencies
├── Dockerfile            # Dockerfile for the application
├── docker-compose.yml    # Docker Compose for local development
├── README.md             # This file
└── .env.example          # Example environment variables
```

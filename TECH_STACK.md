# RAG Multi-Document System - Complete Tech Stack

## **Project Overview**
Multi-document Retrieval-Augmented Generation (RAG) system for intelligent document analysis, semantic search, and entity-aware question answering.

---

## **FRONTEND STACK**

### **Framework & Runtime**
- **React** `^18.2.0` — UI component library
- **Node.js** — JavaScript runtime environment
- **React DOM** `^18.2.0` — React web renderer

### **HTTP & API**
- **Axios** `^1.6.5` — HTTP client for backend communication

### **Document Handling**
- **React PDF** `^7.7.0` — PDF viewer/renderer in browser
- **React Dropzone** `^14.2.3` — File upload with drag-and-drop

### **UI/Icons**
- **Lucide React** `^0.300.0` — Icon library

### **Build Tools**
- **React Scripts** — Webpack-based build toolchain
- **PostCSS** — CSS post-processing
- **Tailwind CSS** — Utility-first CSS framework
- **Webpack** — Module bundler (implicit in react-scripts)

### **Styling**
- **CSS Modules** — Scoped CSS files (Chat.css, Upload.css)
- **Tailwind CSS** — Utility classes (tailwind.config.js)

---

## **BACKEND STACK**

### **Runtime & Server**
- **Python 3.13** — Programming language
- **FastAPI** `0.115.0` — Async web framework
- **Uvicorn** `0.32.0` — ASGI server (handles --reload, MPS GPU)

### **HTTP & Data**
- **HTTPX** `0.27.0` — Async HTTP client (for external Qwen API)
- **Pydantic** `2.10.0` — Data validation & serialization
- **Python-multipart** `0.0.12` — Form data parsing

### **Environment**
- **Python-dotenv** `1.0.0` — Environment variable management (.env)

---

## **RAG PIPELINE STACK**

### **Document Loading & Processing**
- **PyPDF** `5.1.0` — PDF text extraction, metadata parsing
- **LangChain** `0.1.0` — LLM orchestration framework
- **LangChain-Core** `0.1.10` — Core abstractions (Document, chains)

### **Text Chunking**
- **LangChain Text Splitters** — RecursiveCharacterTextSplitter
- **Custom Chunking Logic** — Semantic paragraph-based chunking
  - Token-aware splitting (400 tokens/chunk)
  - Paragraph-aware boundaries
  - Section title detection

### **Embeddings & Semantic Search**
- **Sentence Transformers** `3.3.1` — Embedding models
  - **all-MiniLM-L6-v2** (384-dimensional, lightweight)
  - Runs on: MPS GPU (Apple Metal Performance Shaders)
  - Batch inference for efficiency

### **Vector Database**
- **ChromaDB** `0.5.23` — Vector database for semantic search
  - **Persistent Storage**: `/backend/data/chromadb/`
  - **Collections**: Stores embeddings + metadata
  - **Supports**: Similarity search, metadata filtering
  - **Schema**: Chunks with rich metadata (entity, organization, roles, etc.)

### **Large Language Model (LLM)**
- **Qwen-2.5-VL** (Remote API)
  - **Type**: Vision-Language Model
  - **Endpoint**: `https://umbellar-mechelle-supernationally.ngrok-free.dev/chat`
  - **Protocol**: HTTP POST with JSON payload
  - **Purpose**: Answer generation from retrieved context
  - **Alternative Available**: Local Ollama integration (rag/llm/ollama_client.py)

---

## **ENTITY EXTRACTION STACK**

### **NLP & Entity Recognition**
- **Regex** — Pattern matching for phone numbers, emails, URLs
- **Heuristic Rules** — Title-case detection, keyword matching
- **Custom Logic** — Multi-line parsing for names, organizations, roles

### **Metadata Management**
- **Dictionary-based** — Flat key-value store for ChromaDB compatibility
- **Pipe-delimited encoding** — Lists serialized as "item1|item2|item3"

---

## **DATABASE & STORAGE**

### **Document Storage**
- **Local Filesystem** — `/backend/data/uploads/` (UUID-named PDFs)
- **Metadata JSON** — `/backend/data/metadata.json` (document registry)

### **Vector Storage**
- **ChromaDB** (SQLite-backed) — `/backend/data/chromadb/chroma.sqlite3`
- **Collections Schema**:
  ```json
  {
    "id": "doc-uuid_chunk-idx",
    "document": "chunk text",
    "embedding": [384-dim vector],
    "metadata": {
      "file_name": "resume_job.pdf",
      "primary_entity": "Gopidi Rishith Reddy",
      "entity_persons": "Person1|Person2",
      "entity_organizations": "Org1|Org2",
      "page_number": "1",
      "section_title": "Experience"
    }
  }
  ```

### **Chat History**
- **JSON File** — `/backend/data/chat_history.json`
- **Structure**: Messages with timestamps, document context, sources

---

## **PROJECT STRUCTURE**

```
RAG-Multidocument/
├── frontend/                          # React UI
│   ├── src/
│   │   ├── components/               # React components
│   │   │   ├── Chat.jsx              # Chat interface
│   │   │   ├── Upload.jsx            # Document upload
│   │   │   ├── FileList.jsx          # Document list
│   │   │   ├── PDFViewer.jsx         # PDF rendering
│   │   │   ├── MessageBubble.jsx     # Chat messages
│   │   │   └── ...
│   │   ├── services/
│   │   │   └── api.js               # HTTP client (Axios)
│   │   ├── hooks/
│   │   │   └── useResizablePanels.js # UI state
│   │   ├── App.js                   # Root component
│   │   └── index.js                 # Entry point
│   ├── package.json                 # Dependencies
│   ├── tailwind.config.js           # CSS config
│   └── postcss.config.js            # PostCSS config
│
├── backend/                           # Python FastAPI server
│   ├── main.py                       # Entry point, route setup
│   ├── config.py                     # Configuration
│   ├── requirements.txt              # Python dependencies
│   │
│   ├── rag/                          # RAG Pipeline
│   │   ├── loader.py                 # PDF/TXT loading + entity extraction
│   │   ├── chunker.py                # Semantic text chunking
│   │   ├── embedder.py               # Embedding generation
│   │   ├── vectordb.py               # ChromaDB operations
│   │   ├── retriever.py              # Document retrieval + formatting
│   │   ├── generator.py              # LLM prompt + answer generation
│   │   └── pipeline.py               # Orchestration
│   │
│   ├── llm/                          # LLM Integrations
│   │   └── ollama_client.py          # Local Ollama (alternative)
│   │
│   ├── routes/                       # API endpoints
│   │   ├── upload.py                 # POST /upload
│   │   ├── chat.py                   # POST /chat
│   │   └── debug.py                  # Debugging endpoints
│   │
│   ├── services/                     # Business logic
│   │   ├── document_service.py       # Document CRUD
│   │   └── chat_service.py           # Chat history & context
│   │
│   ├── schemas/                      # Pydantic models
│   │   └── chat.py                   # Request/response schemas
│   │
│   ├── data/                         # Persistent storage
│   │   ├── documents/                # Processed documents
│   │   ├── uploads/                  # Original uploaded files
│   │   ├── chromadb/                 # Vector database
│   │   ├── chat_history.json         # Chat history
│   │   └── metadata.json             # Document metadata registry
│   │
│   └── venv-rag/                     # Virtual environment (Python 3.13)
│
└── README.md                         # Project documentation
```

---

## **DATA FLOW ARCHITECTURE**

```
User Upload (Frontend)
    ↓
[FastAPI: /upload endpoint]
    ↓
[Document Service: Store file + metadata]
    ↓
[RAG Pipeline]
    ├─→ Loader: Extract text + entities (regex + heuristics)
    ├─→ Chunker: Semantic splitting (LangChain)
    ├─→ Embedder: Generate vectors (SentenceTransformers on MPS GPU)
    └─→ VectorDB: Store in ChromaDB (with sanitized metadata)
    ↓
User Query (Frontend)
    ↓
[FastAPI: /chat endpoint]
    ↓
[RAG Pipeline]
    ├─→ Retriever: Query ChromaDB (similarity search)
    ├─→ Formatter: Present results with entity context
    └─→ Generator: Call Qwen API for answer
    ↓
[Response: Answer + Sources + Chat History]
```

---

## **KEY TECHNOLOGIES & VERSIONS**

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Frontend** | React | 18.2.0 | UI |
| **Backend** | FastAPI | 0.115.0 | API Server |
| **Embeddings** | Sentence Transformers | 3.3.1 | Vector Generation |
| **Vector DB** | ChromaDB | 0.5.23 | Semantic Search |
| **Document** | PyPDF | 5.1.0 | PDF Parsing |
| **LLM Framework** | LangChain | 0.1.0 | Orchestration |
| **LLM** | Qwen-2.5-VL | Remote | Generation |
| **HTTP** | HTTPX | 0.27.0 | Async requests |
| **Data** | Pydantic | 2.10.0 | Validation |
| **GPU** | Apple MPS | Implicit | Acceleration |

---

## **DEPLOYMENT & INFRASTRUCTURE**

### **Local Development**
- **Frontend**: `npm run start` (http://localhost:3000)
- **Backend**: `python -m uvicorn main:app --reload --port 8000`
- **Vector DB**: Local SQLite (ChromaDB)
- **Hardware**: MacBook (Apple Silicon, MPS GPU)

### **Production Considerations**
- **LLM**: Remote Qwen API (via ngrok tunnel)
- **Scalability**: Can handle 200-500 PDFs with local ChromaDB
- **Beyond 500 PDFs**: Migrate to cloud vector DB (Pinecone, Weaviate)

---

## **SPECIAL FEATURES**

### **Intelligent Entity Extraction**
- Extracts: Person names, organizations, roles
- Stores in metadata for attribution-aware responses
- Prevents filename-based misattribution

### **Semantic Chunking**
- 400-token chunks with 80-token overlap
- Paragraph-aware splitting
- Section title detection

### **Multi-Document Reasoning**
- Filters documents by entity
- Maintains entity context through pipeline
- Provides source attribution

### **Chat Context Management**
- Stores conversation history (JSON)
- Retrieves document context per query
- Tracks sources for transparency

---

## **DEVELOPMENT TOOLS**

- **Version Control**: Git/GitHub
- **Package Management**: pip (Python), npm (Node.js)
- **Environment**: Virtual environment (Python 3.13)
- **Code Editor**: VS Code (implied)
- **API Testing**: Available via frontend or curl

---

## **SECURITY & COMPATIBILITY**

✅ **Type Safety**: Pydantic for request validation
✅ **Async I/O**: FastAPI + HTTPX for non-blocking operations
✅ **GPU Support**: MPS (Apple Metal) for local acceleration
✅ **File Handling**: Secure upload with UUID-based naming
✅ **Metadata Sanitization**: ChromaDB-compatible flat metadata

---

## **FUTURE ENHANCEMENT PATHS**

1. **NLP Models**: Spacy/Hugging Face for advanced NER
2. **Reranking**: Cross-encoder for better retrieval
3. **Cloud**: AWS/GCP deployment with managed vector DB
4. **Caching**: Redis for query caching
5. **Authentication**: OAuth/JWT for production
6. **Monitoring**: Logging & metrics (Prometheus, ELK)

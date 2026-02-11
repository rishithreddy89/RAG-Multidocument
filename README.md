# 🧠 Multi-Document Reasoning Engine

**Phase 1: Chat + Document Upload**

An advanced Retrieval-Augmented Generation (RAG) system that helps users understand information spread across multiple documents. Phase 1 establishes the foundation with chat capabilities and document storage.

---

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Usage](#usage)
- [Phase 2 Roadmap](#phase-2-roadmap)
- [Troubleshooting](#troubleshooting)

---

## ✨ Features

### Phase 1 (Current)
- ✅ Chat with locally running Qwen-2.5 LLM via Ollama
- ✅ Upload multiple documents (PDF, TXT)
- ✅ Clean, responsive React UI
- ✅ FastAPI backend with async support
- ✅ Document storage for future RAG implementation

### Phase 2 (Coming Soon)
- 🔄 Document parsing and chunking
- 🔄 Vector embeddings generation
- 🔄 ChromaDB integration for semantic search
- 🔄 RAG-powered responses with source citations
- 🔄 Multi-document reasoning and comparison

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **LLM** | Qwen-2.5 (via Ollama) |
| **Backend** | Python 3.9+, FastAPI |
| **Frontend** | React.js 18, Axios |
| **Future DB** | ChromaDB (Phase 2) |

---

## 📁 Project Structure

```
RAG-Multidocument/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py              # Configuration settings
│   ├── requirements.txt       # Python dependencies
│   ├── llm/
│   │   └── ollama_client.py  # Ollama LLM client
│   ├── routes/
│   │   ├── chat.py           # Chat endpoint
│   │   └── upload.py         # Document upload endpoint
│   ├── schemas/
│   │   └── chat.py           # Pydantic models
│   └── data/
│       └── documents/        # Uploaded documents stored here
│
└── frontend/
    ├── package.json
    ├── public/
    │   └── index.html
    └── src/
        ├── App.js            # Main app component
        ├── index.js          # React entry point
        ├── components/
        │   ├── Chat.jsx      # Chat interface
        │   └── Upload.jsx    # Document upload interface
        └── services/
            └── api.js        # Backend API client
```

---

## 🔧 Prerequisites

Before you begin, ensure you have the following installed:

1. **Python 3.9 or higher**
   ```bash
   python3 --version
   ```

2. **Node.js 16+ and npm**
   ```bash
   node --version
   npm --version
   ```

3. **Ollama** (for local LLM)
   - Install from: https://ollama.ai
   - Or use Homebrew on macOS:
     ```bash
     brew install ollama
     ```

---

## 📦 Installation

### Step 1: Install Ollama and Qwen-2.5

```bash
# Start Ollama service (run in a separate terminal)
ollama serve

# In another terminal, pull the Qwen-2.5 model
ollama pull qwen2.5
```

> **Note:** The first time you pull the model, it will download several GB of data. This may take a few minutes.

### Step 2: Set Up Backend

```bash
# Navigate to backend directory
cd backend

# Create a virtual environment (recommended)
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### Step 3: Set Up Frontend

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install Node.js dependencies
npm install
```

---

## 🚀 Running the Application

You'll need **three terminal windows** open:

### Terminal 1: Ollama Service

```bash
ollama serve
```

Keep this running in the background. You should see:
```
Ollama is running on http://localhost:11434
```

### Terminal 2: Backend Server

```bash
cd backend

# Activate virtual environment if not already active
source venv/bin/activate

# Run the FastAPI server
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will start at: **http://localhost:8000**

You can view the API docs at: **http://localhost:8000/docs**

### Terminal 3: Frontend Server

```bash
cd frontend

# Start the React development server
npm start
```

The frontend will automatically open at: **http://localhost:3000**

---

## 🎯 Usage

### Chatting with the LLM

1. Open **http://localhost:3000** in your browser
2. Click the **💬 Chat** tab
3. Type your message in the input box
4. Press **Enter** or click **📤 Send**
5. Wait for the LLM to respond

**Example questions:**
- "What is quantum computing?"
- "Explain how neural networks work"
- "Write a Python function to calculate fibonacci numbers"

### Uploading Documents

1. Click the **📁 Upload** tab
2. Click **📎 Choose Files**
3. Select one or more PDF or TXT files
4. Click **☁️ Upload Documents**
5. You'll see a success message with uploaded file names

**Where are documents stored?**
- Documents are saved in: `backend/data/documents/`
- In Phase 2, they will be automatically processed and indexed

---

## 🔮 Phase 2 Roadmap

The following features will be added in Phase 2:

### Document Processing
- Parse PDF and TXT files
- Split documents into semantic chunks
- Extract metadata (title, author, date)

### Vector Search
- Generate embeddings using sentence-transformers
- Store embeddings in ChromaDB
- Implement semantic similarity search

### RAG Pipeline
- Retrieve relevant document chunks for user queries
- Build context-aware prompts
- Generate responses with source citations
- Support multi-document reasoning

### Enhanced UI
- Display source documents in responses
- Highlight relevant passages
- Document management (view, delete)
- Search history

---

## 🐛 Troubleshooting

### Backend won't start

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Ollama connection error

**Error:** `Cannot connect to Ollama at http://localhost:11434`

**Solution:**
1. Make sure Ollama is running: `ollama serve`
2. Verify the model is installed: `ollama list`
3. If not installed: `ollama pull qwen2.5`

### Frontend can't connect to backend

**Error:** "Cannot connect to backend. Make sure the server is running."

**Solution:**
1. Verify backend is running at http://localhost:8000
2. Check CORS settings in `backend/main.py`
3. Try accessing http://localhost:8000 in your browser

### Port already in use

**Error:** `Address already in use`

**Solution:**
```bash
# Find process using port 8000 (backend)
lsof -i :8000
kill -9 <PID>

# Or for port 3000 (frontend)
lsof -i :3000
kill -9 <PID>
```

### Model responses are slow

This is normal for local LLMs, especially on CPU. Response time depends on:
- Your hardware (GPU recommended)
- Model size
- Prompt length

To speed up responses:
- Use a smaller model: `ollama pull qwen2.5:1.5b`
- Update `backend/config.py` to use the smaller model

---

## 🤝 Contributing

This is Phase 1 of the project. Phase 2 will add RAG capabilities. The codebase is designed to be beginner-friendly with:
- Clear comments explaining each function
- TODO markers for Phase 2 features
- Modular architecture for easy extension

---

## 📝 License

This project is for educational purposes.

---

## 📧 Support

If you encounter any issues:
1. Check the [Troubleshooting](#troubleshooting) section
2. Verify all prerequisites are installed
3. Make sure all three services are running (Ollama, Backend, Frontend)

---

**Built with ❤️ using React + FastAPI + Qwen-2.5**

*Phase 2 coming soon with full RAG capabilities!*

# Car Recommendation RAG Chatbot

RAG-based Indian car recommender built with **Gemini**, **ChromaDB**, **FastAPI**, and **React**.

Repository: [https://github.com/anuj-pnchl/car_recommendation](https://github.com/anuj-pnchl/car_recommendation)

This is a beginner-friendly learning project that shows how **Retrieval-Augmented Generation (RAG)** works end to end — without LangChain, LlamaIndex, agents, or a heavy database stack.

---

## Problem Statement

Buying a car involves many constraints: budget, fuel type, transmission, body style, seating, safety, and lifestyle needs.

Traditional keyword search often fails on natural questions like:

> “Suggest a petrol automatic SUV under 15 lakh for a family of 5”

This project solves that by combining:

1. **Structured filtering** for explicit constraints (price, fuel, transmission, body type, seating)
2. **Semantic retrieval** for intent (family use, mileage, safety, comfort)
3. **Gemini** to generate a grounded recommendation using only retrieved cars from a local dataset

The goal is a simple, explainable car recommendation chatbot that stays faithful to the available data.

---

## Features

- Browse a curated Indian-market car dataset (`data/cars.json`)
- Filter cars by body type, fuel, transmission, and max price
- Convert car text into **Gemini embeddings**
- Store embeddings in a local **ChromaDB** vector store
- **Semantic search** over car documents
- **Hybrid retrieval** (structured filters + semantic ranking)
- **RAG chat** via `POST /api/chat` with grounded Gemini answers
- React chat UI with example questions
- Chat history saved in browser **localStorage** (no backend chat database)
- Clear **no-match** behavior when hard constraints cannot be satisfied

---

## Architecture

```text
React (Vite + Tailwind)
        │  HTTP
        ▼
FastAPI backend
        │
        ├── data/cars.json          (structured car catalog)
        ├── Gemini embeddings       (text → vectors)
        ├── ChromaDB                (local vector store)
        ├── Query parser            (budget / fuel / body / …)
        ├── Hybrid retrieval        (filter + semantic rank)
        └── Gemini chat model       (grounded recommendation)
```

High-level request flow for chat:

```text
User question
  ↓
Extract structured constraints
  ↓
Filter candidate cars from cars.json
  ↓
Semantic retrieval in ChromaDB (among candidates)
  ↓
Build RAG context from matching cars
  ↓
Gemini generates a grounded answer
  ↓
Response + sources (+ extracted filters)
```

---

## Technologies Used

| Layer | Technology |
|-------|------------|
| Frontend | React, Vite, Tailwind CSS |
| Backend | FastAPI, Uvicorn, Pydantic |
| LLM / embeddings | Google Gemini (`google-genai`) |
| Vector store | ChromaDB (local persistent) |
| Dataset | JSON (`data/cars.json`) |
| Chat history | Browser `localStorage` |

**Intentionally not used:** LangChain, LlamaIndex, PostgreSQL, Redis, Elasticsearch, Docker, auth, agents.

---

## Dataset

Source file: [`data/cars.json`](data/cars.json)

- **~30** Indian-market cars (demo dataset)
- Price range roughly **₹7.5 lakh – ₹28 lakh**
- Body types: Hatchback, Sedan, Compact SUV, SUV, MPV
- Fuel types: Petrol, Diesel, CNG, Electric
- Transmissions: Manual, Automatic, AMT, CVT, DCT, e-CVT

Useful fields include:

- `brand`, `model`, `variant`
- `price`, `fuel_type`, `transmission`, `body_type`
- `seating_capacity`, `mileage`, `safety_rating`
- `features`, `suitable_for`, `description`

This dataset is for learning. It is not a live inventory or pricing feed.

---

## Recommendation Approach

### Semantic retrieval

Understands the *meaning* of a question (family use, good mileage, safe car) by comparing Gemini embeddings in ChromaDB.

### Structured filtering

Handles *exact* constraints extracted from the question:

- budget (`under 15 lakh`)
- fuel (`petrol`, `diesel`, `electric`, …)
- transmission (`automatic`, `manual`)
- body type (`SUV`, `sedan`, …)
- seating (`family of 5`, `7 seater`)
- safety keywords (`safe` → rating ≥ 4)

### Hybrid retrieval

1. Parse obvious constraints from the user question
2. Filter `cars.json` with those hard constraints
3. If nothing matches → return a clear no-match message (do **not** recommend unrelated cars)
4. Otherwise rank only the remaining candidates with ChromaDB semantic search
5. Send only those cars to Gemini as RAG context

**Explicit constraints always take priority over semantic similarity.**

Example: `"Petrol automatic SUV under 15 lakh"`

1. Parse → Petrol + automatic gearboxes + SUV/Compact SUV + max price 15 lakh  
2. Keep only matching cars from the dataset  
3. Semantically rank those candidates  
4. Ask Gemini to recommend from that filtered set only  

---

## RAG Architecture

**RAG = Retrieval-Augmented Generation**

1. **Ingest** — turn each car into a text document, embed it with Gemini, store in ChromaDB  
2. **Retrieve** — embed the user question and find relevant car documents (with hybrid filters for chat)  
3. **Augment** — build a prompt that includes only retrieved car facts  
4. **Generate** — Gemini answers using that context and is instructed not to invent specs  

Key endpoints:

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/health` | Backend health check |
| `GET` | `/api/cars` | List/filter cars |
| `POST` | `/api/embeddings` | Embedding demo |
| `GET` | `/api/chroma/status` | Chroma collection status |
| `POST` | `/api/search` | Semantic search only |
| `POST` | `/api/chat` | Hybrid RAG recommendation |

API docs (when backend is running): [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Project Structure

```text
car_recommendation/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app + CORS
│   │   ├── api/                    # Route handlers
│   │   │   ├── cars.py
│   │   │   ├── embeddings.py
│   │   │   ├── chroma.py
│   │   │   ├── search.py
│   │   │   └── chat.py
│   │   ├── schemas/                # Pydantic models
│   │   └── services/               # Business logic
│   │       ├── cars.py
│   │       ├── gemini.py
│   │       ├── embeddings.py
│   │       ├── vector_store.py
│   │       ├── retrieval.py        # Semantic + hybrid search
│   │       ├── query_parser.py     # Constraint extraction
│   │       └── rag.py              # Prompt + Gemini answer
│   ├── scripts/
│   │   ├── ingest_cars.py          # cars.json → ChromaDB
│   │   ├── test_embeddings.py
│   │   └── test_chroma.py
│   ├── chroma_db/                  # Local vector DB (created after ingest)
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── CarsPage.jsx
│   │   │   ├── ChatPage.jsx
│   │   │   └── CarCard.jsx
│   │   ├── config/api.js
│   │   └── utils/chatHistory.js
│   ├── .env.example
│   └── package.json
├── data/
│   └── cars.json
├── .gitignore
└── README.md
```

---

## Installation / Setup

### Prerequisites

- Python **3.10+**
- Node.js **18+** and npm
- A Google **Gemini API key**

### 1. Clone the repository

```bash
git clone https://github.com/anuj-pnchl/car_recommendation.git
cd car_recommendation
```

### 2. Backend setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Frontend setup

```bash
cd frontend
npm install
```

### 4. Environment files

See the next section for the Gemini API key.

Frontend:

```bash
cd frontend
cp .env.example .env
# default: VITE_API_BASE_URL=http://localhost:8000
```

---

## Gemini API Key Setup

1. Create an API key from [Google AI Studio](https://aistudio.google.com/apikey)
2. In the backend folder:

```bash
cd backend
cp .env.example .env
```

3. Edit `backend/.env`:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
GEMINI_CHAT_MODEL=gemini-flash-lite-latest
```

Important:

- Put the key **only** in `backend/.env`
- **Never** put the Gemini key in the React frontend
- **Never** commit `.env` (it is gitignored)

`gemini-flash-lite-latest` is recommended on the free tier to reduce quota / 429 errors.

---

## How to Run the Application

You need **three steps**: ingest cars into ChromaDB, start the backend, start the frontend.

### Step A — Ingest car documents into ChromaDB

Run once after setup (and again if `cars.json` changes):

```bash
cd backend
source .venv/bin/activate
python scripts/ingest_cars.py
```

This embeds each car with Gemini and stores documents in `backend/chroma_db/`.

Optional checks:

```bash
python scripts/test_chroma.py
```

### Step B — Start the backend

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Health: [http://localhost:8000/api/health](http://localhost:8000/api/health)
- Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Chroma status: [http://localhost:8000/api/chroma/status](http://localhost:8000/api/chroma/status)

### Step C — Start the frontend

Open a second terminal:

```bash
cd frontend
npm run dev
```

Open: [http://localhost:5173](http://localhost:5173)

Use the **Cars** tab to browse/filter cars and the **Chat** tab for RAG recommendations.

### Quick API examples

```bash
# Health
curl http://localhost:8000/api/health

# Semantic search
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{"query":"Suggest a family SUV under 15 lakh","top_k":5}'

# RAG chat (hybrid)
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message":"Suggest a petrol automatic SUV under 15 lakh for a family of 5","top_k":5}'
```

---

## Example Queries

Try these in the Chat UI or via `POST /api/chat`:

1. `Suggest a family SUV under 15 lakh`
2. `I want a petrol automatic car under 12 lakh`
3. `Suggest a diesel SUV`
4. `I need an electric car`
5. `I need a car for 5 people`
6. `Suggest a safe family car`
7. `Give me a sedan under 10 lakh`
8. `Suggest a car with good mileage`
9. `Suggest an automatic SUV under 8 lakh` ← often **no match** in this dataset
10. `Suggest a petrol automatic SUV under 15 lakh for a family of 5`

Expected behavior:

- Hard filters (budget/fuel/body/etc.) are respected
- If nothing matches all constraints, the assistant says so clearly
- Answers should stay grounded in the retrieved cars

---

## Limitations

- Small demo dataset (~30 cars), not real-time market data
- Simple keyword/regex constraint parser — not full NLP
- Free-tier Gemini may hit rate limits / daily quotas
- Chat history is browser-only (`localStorage`), not multi-device
- No multi-turn conversation memory sent to Gemini yet
- No user accounts, payments, or dealer integrations
- “Automatic” maps to multiple gearbox types (AMT/CVT/DCT/e-CVT)
- “SUV” includes Compact SUV in filtering

---

## Future Improvements

- Multi-turn chat context (short conversation memory)
- Better natural-language constraint extraction
- Richer dataset / more attributes (ownership cost, city vs highway)
- Comparison mode (“A vs B”)
- Streaming chat responses
- Soft preferences (mileage/safety) with transparent ranking explanation
- Deploy backend + frontend (still keeping local/dev setup simple)

---

## Key Learnings

- **Embeddings** turn text into vectors so similar meaning can be searched
- **Vector databases** (ChromaDB) store and retrieve those vectors locally
- **RAG** reduces hallucinations by grounding answers in retrieved documents
- **Hybrid retrieval** is often better than semantic search alone for hard constraints like budget and fuel type
- Keeping the stack simple (FastAPI + Gemini + Chroma + React) makes each RAG step easy to understand
- Secrets belong only on the backend; the frontend should never hold the LLM API key

---

## License

This project is intended for learning and portfolio use. Add a license file if you want to clarify reuse terms.

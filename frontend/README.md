# Frontend — Car Recommendation RAG Chatbot

React + Vite + Tailwind UI for the learning project.

## Setup

```bash
cd frontend
npm install
cp .env.example .env   # optional; defaults to http://localhost:8000
```

## Run

```bash
npm run dev
```

Open http://localhost:5173

Make sure the FastAPI backend is running on port 8000.

## Pages

- **Chat** — ask questions via `POST /api/chat` (RAG)
- **Cars** — list/filter cars from `GET /api/cars`
- **Backend Check** — `GET /api/health`

## Chat history (browser only)

Messages are saved in `localStorage` under:

```text
car-rag-chat-history
```

- Refresh restores the conversation.
- **Clear Chat** removes it from the UI and from localStorage.
- Nothing is stored on the server.

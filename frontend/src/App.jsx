import { useState } from 'react'
import CarsPage from './components/CarsPage'
import ChatPage from './components/ChatPage'
import { API_BASE_URL } from './config/api'

function App() {
  // Simple view switch — no router library needed.
  const [view, setView] = useState('chat') // 'chat' | 'cars' | 'health'

  // Health-check state (Step 1)
  const [status, setStatus] = useState('idle')
  const [message, setMessage] = useState('')

  async function checkBackend() {
    setStatus('loading')
    setMessage('')

    try {
      const response = await fetch(`${API_BASE_URL}/api/health`)

      if (!response.ok) {
        throw new Error(`Server responded with status ${response.status}`)
      }

      const data = await response.json()
      setStatus('success')
      setMessage(data.message || 'Backend is reachable')
    } catch (error) {
      setStatus('error')
      setMessage(
        error.message ||
          'Could not reach the backend. Is FastAPI running on port 8000?'
      )
    }
  }

  const navButtonClass = (active) =>
    `px-4 py-2 text-sm font-medium ${
      active
        ? 'bg-blue-600 text-white'
        : 'bg-white text-slate-700 border border-slate-300'
    }`

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-4">
          <div className="text-left">
            <h1 className="text-xl font-bold text-slate-900 sm:text-2xl">
              Car Recommendation RAG Chatbot
            </h1>
            <p className="text-sm text-slate-600">
              Learning RAG with Gemini + ChromaDB
            </p>
          </div>

          <nav className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => setView('chat')}
              className={navButtonClass(view === 'chat')}
            >
              Chat
            </button>
            <button
              type="button"
              onClick={() => setView('cars')}
              className={navButtonClass(view === 'cars')}
            >
              Cars
            </button>
            <button
              type="button"
              onClick={() => setView('health')}
              className={navButtonClass(view === 'health')}
            >
              Backend Check
            </button>
          </nav>
        </div>
      </header>

      {view === 'chat' && <ChatPage />}
      {view === 'cars' && <CarsPage />}

      {view === 'health' && (
        <main className="mx-auto max-w-xl px-4 py-12 text-center">
          <h2 className="text-2xl font-bold text-slate-900 mb-2">
            Backend Connectivity
          </h2>
          <p className="text-slate-600 mb-8">
            Step 1 check — confirm FastAPI is reachable.
          </p>

          <button
            type="button"
            onClick={checkBackend}
            disabled={status === 'loading'}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-medium px-6 py-3 transition-colors"
          >
            {status === 'loading' ? 'Checking…' : 'Check Backend'}
          </button>

          {status === 'success' && (
            <div className="mt-8 p-4 border border-green-200 bg-green-50 text-left">
              <p className="font-semibold text-green-800">
                Backend Status: Connected
              </p>
              <p className="text-green-700 mt-1">{message}</p>
            </div>
          )}

          {status === 'error' && (
            <div className="mt-8 p-4 border border-red-200 bg-red-50 text-left">
              <p className="font-semibold text-red-800">
                Backend Status: Not Connected
              </p>
              <p className="text-red-700 mt-1">{message}</p>
              <p className="text-red-600 text-sm mt-2">
                Make sure the backend is running:{' '}
                <code className="bg-red-100 px-1">
                  uvicorn app.main:app --reload --port 8000
                </code>
              </p>
            </div>
          )}
        </main>
      )}
    </div>
  )
}

export default App

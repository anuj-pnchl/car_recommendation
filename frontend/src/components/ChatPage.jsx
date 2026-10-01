import { useEffect, useRef, useState } from 'react'
import { API_BASE_URL } from '../config/api'
import {
  clearChatHistory,
  loadChatHistory,
  saveChatHistory,
} from '../utils/chatHistory'

const EXAMPLE_QUESTIONS = [
  'Suggest a family SUV under 15 lakh',
  'I want a petrol automatic car',
  'Which cars have good safety?',
  'Suggest a car for a family of 5',
]

/**
 * Chat page — sends user questions to POST /api/chat (RAG backend).
 * Conversation is persisted in browser localStorage only.
 */
function ChatPage() {
  const [messages, setMessages] = useState(() => loadChatHistory())
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)
  const textareaRef = useRef(null)

  // Keep localStorage in sync whenever messages change.
  useEffect(() => {
    saveChatHistory(messages)
  }, [messages])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  async function sendMessage(rawText) {
    const text = (rawText || '').trim()
    if (!text || loading) return

    const userMessage = { role: 'user', content: text }
    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      })

      if (!response.ok) {
        let detail = ''
        try {
          const errBody = await response.json()
          detail = errBody.detail || ''
        } catch {
          // ignore JSON parse errors
        }
        throw new Error(
          typeof detail === 'string' && detail
            ? detail
            : `Server responded with status ${response.status}`
        )
      }

      const data = await response.json()
      const answer =
        (data.response || '').trim() ||
        'Sorry, I received an empty response. Please try again.'

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: answer,
        },
      ])
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content:
            "Sorry, I couldn't get a response. Please try again. Make sure the backend is running on port 8000.",
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  function handleClearChat() {
    if (messages.length === 0) return
    const confirmed = window.confirm(
      'Clear the entire chat history from this browser?'
    )
    if (!confirmed) return

    setMessages([])
    clearChatHistory()
  }

  function handleSubmit(event) {
    event.preventDefault()
    sendMessage(input)
  }

  function handleKeyDown(event) {
    // Enter sends; Shift+Enter inserts a new line.
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      sendMessage(input)
    }
  }

  return (
    <section className="mx-auto flex w-full max-w-3xl flex-col px-4 py-6 min-h-[calc(100vh-5.5rem)]">
      <div className="mb-4 flex flex-wrap items-start justify-between gap-3 text-left">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">
            Car Recommendation Assistant
          </h2>
          <p className="mt-1 text-sm text-slate-600">
            Ask about budget, fuel type, body type, mileage, safety, and more.
            Answers are based on the cars stored in ChromaDB.
          </p>
        </div>

        <button
          type="button"
          onClick={handleClearChat}
          disabled={messages.length === 0 || loading}
          className="border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Clear Chat
        </button>
      </div>

      <div className="flex flex-1 flex-col border border-slate-200 bg-white">
        {/* Message list */}
        <div className="flex-1 space-y-4 overflow-y-auto p-4 text-left">
          {messages.length === 0 && !loading && (
            <div className="space-y-4">
              <p className="text-slate-700">
                Hi! I can help you find a car based on your budget, fuel type,
                body type, mileage, safety, and other available car information.
              </p>
              <div>
                <p className="mb-2 text-sm font-medium text-slate-600">
                  Try an example:
                </p>
                <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap">
                  {EXAMPLE_QUESTIONS.map((question) => (
                    <button
                      key={question}
                      type="button"
                      onClick={() => sendMessage(question)}
                      disabled={loading}
                      className="border border-slate-300 bg-slate-50 px-3 py-2 text-left text-sm text-slate-800 hover:bg-slate-100 disabled:opacity-50"
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {messages.map((message, index) => (
            <div
              key={`${message.role}-${index}`}
              className={`max-w-[95%] sm:max-w-[85%] whitespace-pre-wrap rounded-none px-3 py-2 text-sm leading-relaxed ${
                message.role === 'user'
                  ? 'ml-auto bg-blue-600 text-white'
                  : 'mr-auto bg-slate-100 text-slate-900'
              }`}
            >
              <p className="mb-1 text-xs font-semibold opacity-80">
                {message.role === 'user' ? 'You' : 'Assistant'}
              </p>
              <p>{message.content}</p>
            </div>
          ))}

          {loading && (
            <div className="mr-auto max-w-[85%] bg-slate-100 px-3 py-2 text-sm text-slate-600">
              Assistant is thinking…
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <form
          onSubmit={handleSubmit}
          className="border-t border-slate-200 p-3"
        >
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end">
            <label className="sr-only" htmlFor="chat-input">
              Your question
            </label>
            <textarea
              id="chat-input"
              ref={textareaRef}
              rows={2}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
              placeholder="Type your question… (Enter to send, Shift+Enter for new line)"
              className="w-full flex-1 resize-y border border-slate-300 px-3 py-2 text-sm text-slate-900 disabled:bg-slate-50"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="bg-blue-600 px-5 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:bg-blue-300 sm:min-w-[6rem]"
            >
              {loading ? 'Sending…' : 'Send'}
            </button>
          </div>
        </form>
      </div>
    </section>
  )
}

export default ChatPage

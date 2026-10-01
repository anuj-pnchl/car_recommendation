/**
 * Browser-only chat history helpers (localStorage).
 * Does not talk to the backend or store API keys / embeddings.
 */

export const CHAT_HISTORY_KEY = 'car-rag-chat-history'

/**
 * Normalize and validate stored messages.
 * Only keeps { role, content } for user/assistant.
 */
export function sanitizeMessages(value) {
  if (!Array.isArray(value)) return []

  return value
    .filter(
      (item) =>
        item &&
        typeof item === 'object' &&
        (item.role === 'user' || item.role === 'assistant') &&
        typeof item.content === 'string' &&
        item.content.trim().length > 0
    )
    .map((item) => ({
      role: item.role,
      content: item.content,
    }))
}

export function loadChatHistory() {
  try {
    if (typeof localStorage === 'undefined') return []

    const raw = localStorage.getItem(CHAT_HISTORY_KEY)
    if (!raw) return []

    const parsed = JSON.parse(raw)
    return sanitizeMessages(parsed)
  } catch {
    // Invalid JSON / blocked storage — start fresh.
    return []
  }
}

export function saveChatHistory(messages) {
  try {
    if (typeof localStorage === 'undefined') return

    const toStore = sanitizeMessages(messages)
    localStorage.setItem(CHAT_HISTORY_KEY, JSON.stringify(toStore))
  } catch {
    // Quota exceeded / private mode — chat still works in-memory.
  }
}

export function clearChatHistory() {
  try {
    if (typeof localStorage === 'undefined') return
    localStorage.removeItem(CHAT_HISTORY_KEY)
  } catch {
    // Ignore clear failures.
  }
}

/**
 * Shared frontend API base URL.
 * Set VITE_API_BASE_URL in frontend/.env if needed.
 * Never put the Gemini API key in the frontend.
 */
export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

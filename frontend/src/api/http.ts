import { readAccessToken } from '../auth/tokenStorage'

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '')

export class ApiError extends Error {
  public readonly status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

// Centralizing fetch keeps URL, JSON, bearer token, and error handling consistent.
export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
  needsAuthentication = true,
): Promise<T> {
  const headers = new Headers(options.headers)
  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  // Only protected endpoints receive a token; auth endpoints opt out explicitly.
  if (needsAuthentication) {
    const token = readAccessToken()
    if (token) headers.set('Authorization', `Bearer ${token}`)
  }

  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers })
  } catch {
    throw new ApiError('Cannot reach the backend. Check that FastAPI is running.', 0)
  }

  if (!response.ok) {
    const body: unknown = await response.json().catch(() => null)
    throw new ApiError(getErrorMessage(response.status, body), response.status)
  }

  // DELETE returns 204 without a response body.
  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

function getErrorMessage(status: number, body: unknown): string {
  if (status === 401) return 'Email or password is incorrect, or your session has expired.'
  if (status === 404) return 'That application was not found.'
  if (status === 409) return 'That email address is already registered.'

  if (typeof body === 'object' && body !== null && 'detail' in body) {
    const detail = body.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) {
      return `Please check the submitted fields: ${detail.map((item) => {
        if (typeof item !== 'object' || item === null || !('msg' in item)) return 'Invalid input'
        return String(item.msg)
      }).join('; ')}`
    }
  }
  return `The server could not complete the request (HTTP ${status}). Please try again.`
}

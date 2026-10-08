const TOKEN_KEY = 'job_application_tracker_token'

// localStorage keeps this learning app signed in when the page is refreshed.
export function readAccessToken(): string | null {
  return typeof localStorage === 'undefined' ? null : localStorage.getItem(TOKEN_KEY)
}

export function saveAccessToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearAccessToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}

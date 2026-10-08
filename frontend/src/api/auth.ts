import { apiRequest } from './http'

export interface UserResponse {
  id: number
  email: string
  created_at: string
}

export interface TokenResponse {
  access_token: string
  token_type: 'bearer'
}

export function registerUser(email: string, password: string): Promise<UserResponse> {
  return apiRequest<UserResponse>('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  }, false)
}

export function loginUser(email: string, password: string): Promise<TokenResponse> {
  return apiRequest<TokenResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  }, false)
}

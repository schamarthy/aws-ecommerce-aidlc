import axios from 'axios'
import type { TokenResponse, User } from '../types/user'

const api = axios.create({ baseURL: '/auth' })

function getToken(): string | null {
  return localStorage.getItem('auth_token')
}

function authHeaders() {
  const token = getToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export const authApi = {
  register: (name: string, email: string, password: string) =>
    api.post<TokenResponse>('/register', { name, email, password }).then(r => r.data),

  login: (email: string, password: string) =>
    api.post<TokenResponse>('/login', { email, password }).then(r => r.data),

  getMe: () =>
    api.get<User>('/me', { headers: authHeaders() }).then(r => r.data),

  updateProfile: (name: string) =>
    api.patch<User>('/me', { name }, { headers: authHeaders() }).then(r => r.data),
}

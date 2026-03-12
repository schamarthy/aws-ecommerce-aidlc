import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { authApi } from '../api/auth'
import type { User } from '../types/user'

interface AuthContextValue {
  user: User | null
  token: string | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (name: string, email: string, password: string) => Promise<void>
  logout: () => void
  updateProfile: (name: string) => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(localStorage.getItem('auth_token'))
  const [loading, setLoading] = useState(!!localStorage.getItem('auth_token'))

  useEffect(() => {
    if (token) {
      authApi.getMe()
        .then(setUser)
        .catch(() => {
          // Token invalid or expired — clear it
          localStorage.removeItem('auth_token')
          setToken(null)
        })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [token])

  const login = useCallback(async (email: string, password: string) => {
    const data = await authApi.login(email, password)
    localStorage.setItem('auth_token', data.access_token)
    setToken(data.access_token)
    setUser(data.user)
  }, [])

  const register = useCallback(async (name: string, email: string, password: string) => {
    const data = await authApi.register(name, email, password)
    localStorage.setItem('auth_token', data.access_token)
    setToken(data.access_token)
    setUser(data.user)
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('auth_token')
    setToken(null)
    setUser(null)
  }, [])

  const updateProfile = useCallback(async (name: string) => {
    const updated = await authApi.updateProfile(name)
    setUser(updated)
  }, [])

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout, updateProfile }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}

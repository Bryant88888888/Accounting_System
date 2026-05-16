"use client"

import { createContext, useContext, useEffect, useState, ReactNode } from "react"
import { AuthUser } from "@/types/auth"
import { loginApi, getMeApi } from "@/lib/api/auth"

interface AuthContextValue {
  user: AuthUser | null
  isLoading: boolean
  login: (account: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem("token")
    if (!token) {
      setIsLoading(false)
      return
    }
    getMeApi()
      .then(setUser)
      .catch(() => localStorage.removeItem("token"))
      .finally(() => setIsLoading(false))
  }, [])

  async function login(account: string, password: string) {
    const res = await loginApi(account, password)
    localStorage.setItem("token", res.access_token)
    setUser(res.account)
  }

  function logout() {
    localStorage.removeItem("token")
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error("useAuth must be used within AuthProvider")
  return ctx
}

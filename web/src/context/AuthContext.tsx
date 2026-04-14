/* eslint-disable react-refresh/only-export-components */
import {
  createContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from "react"
import { useQueryClient } from "@tanstack/react-query"
import type { User } from "@/types/auth"
import {
  getStoredTokens,
  setStoredTokens,
  clearStoredTokens,
  type StoredTokens,
} from "@/lib/api-client"
import { getMe, logout as logoutApi } from "@/lib/auth-api"

export interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (tokens: StoredTokens) => Promise<void>
  logout: () => Promise<void>
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const queryClient = useQueryClient()

  // Check auth status on mount
  useEffect(() => {
    let isMounted = true

    const checkAuth = async () => {
      const tokens = getStoredTokens()
      if (tokens?.access) {
        try {
          const userData = await getMe()
          if (isMounted) {
            setUser(userData)
          }
        } catch {
          clearStoredTokens()
          if (isMounted) {
            setUser(null)
          }
        }
      }
      if (isMounted) {
        setIsLoading(false)
      }
    }

    checkAuth()

    return () => {
      isMounted = false
    }
  }, [])

  const login = useCallback(async (tokens: StoredTokens) => {
    setStoredTokens(tokens)
    try {
      const userData = await getMe()
      setUser(userData)
    } catch {
      clearStoredTokens()
      setUser(null)
    }
  }, [])

  const logout = useCallback(async () => {
    // Try to blacklist the refresh token on the server
    const tokens = getStoredTokens()
    if (tokens?.refresh) {
      try {
        await logoutApi(tokens.refresh)
      } catch {
        // Ignore errors - we still want to clear local tokens
      }
    }
    clearStoredTokens()
    setUser(null)
    queryClient.clear()
  }, [queryClient])

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

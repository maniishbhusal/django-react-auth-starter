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
  setAccessToken,
  clearAccessToken,
} from "@/lib/api-client"
import {
  getMe,
  logout as logoutApi,
  refreshToken as refreshTokenApi,
} from "@/lib/auth-api"

export interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (access: string) => Promise<void>
  logout: () => Promise<void>
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const queryClient = useQueryClient()

  // Bootstrap: try silent refresh using the httpOnly cookie. If it succeeds,
  // we have a valid session; if it 401s, the user is logged out.
  useEffect(() => {
    let isMounted = true

    const checkAuth = async () => {
      try {
        const { access } = await refreshTokenApi()
        setAccessToken(access)
        const userData = await getMe()
        if (isMounted) setUser(userData)
      } catch {
        clearAccessToken()
        if (isMounted) setUser(null)
      } finally {
        if (isMounted) setIsLoading(false)
      }
    }

    checkAuth()

    return () => {
      isMounted = false
    }
  }, [])

  const login = useCallback(async (access: string) => {
    setAccessToken(access)
    try {
      const userData = await getMe()
      setUser(userData)
    } catch {
      clearAccessToken()
      setUser(null)
    }
  }, [])

  const logout = useCallback(async () => {
    try {
      await logoutApi()
    } catch {
      // Logout is idempotent server-side; clear local state regardless.
    }
    clearAccessToken()
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

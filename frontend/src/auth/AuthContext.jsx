import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { getCurrentUser, login, logout } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  const refreshUser = useCallback(async () => {
    setLoading(true)
    try {
      const currentUser = await getCurrentUser()
      setUser(currentUser)
      return currentUser
    } catch {
      setUser(null)
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    // Clear credentials left behind by versions that used browser storage.
    localStorage.removeItem('token')
    localStorage.removeItem('role')
    refreshUser()
  }, [refreshUser])

  const signIn = useCallback(async (username, password) => {
    const currentUser = await login(username, password)
    setUser(currentUser)
    return currentUser
  }, [])

  const signOut = useCallback(async () => {
    await logout()
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({ user, loading, refreshUser, signIn, signOut }),
    [loading, refreshUser, signIn, signOut, user],
  )
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within an AuthProvider')
  return context
}

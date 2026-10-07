import { useEffect, useMemo, useState } from 'react'

import { AuthContext } from '@/features/auth/context/AuthContext'
import { apiClient, clearAuthTokens, getAccessToken } from '@/shared/api/apiClient'
import { logoutClientSession } from '@/features/auth/api/authService'

const initialAuthState = Object.freeze({
  status: 'checking',
  user: null,
})

export function AuthProvider({ children }) {
  const [authState, setAuthState] = useState(initialAuthState)

  useEffect(() => {
    let isActive = true

    async function hydrateSession() {
      const token = getAccessToken()

      if (!token) {
        if (isActive) {
          setAuthState({ status: 'unauthenticated', user: null })
        }
        return
      }

      try {
        const { data } = await apiClient.get('/auth/me')

        if (isActive) {
          setAuthState({ status: 'authenticated', user: data })
        }
      } catch {
        clearAuthTokens()

        if (isActive) {
          setAuthState({ status: 'unauthenticated', user: null })
        }
      }
    }

    hydrateSession()

    return () => {
      isActive = false
    }
  }, [])

  const value = useMemo(
    () => ({
      ...authState,
      clearSession: async () => {
        await logoutClientSession().catch(() => {})
        clearAuthTokens()
        setAuthState({ status: 'unauthenticated', user: null })
      },
      establishSession: (user) => setAuthState({ status: 'authenticated', user }),
      isAuthenticated: authState.status === 'authenticated',
    }),
    [authState],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

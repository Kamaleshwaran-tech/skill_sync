import { apiClient, clearAuthTokens, setAuthTokens } from '@/shared/api/apiClient'

export class AuthIntegrationUnavailableError extends Error {
  constructor() {
    super('Authentication is not connected yet. Please try again after the backend integration is available.')
    this.name = 'AuthIntegrationUnavailableError'
  }
}

function createUnavailableGateway() {
  const unavailable = async () => {
    throw new AuthIntegrationUnavailableError()
  }

  return {
    requestPasswordReset: unavailable,
    signIn: unavailable,
    signUp: unavailable,
  }
}

async function getCurrentUser() {
  const { data } = await apiClient.get('/auth/me')
  return data
}

export function createAuthService(gateway = createUnavailableGateway()) {
  const signIn = async (credentials) => {
    const response = await gateway.signIn(credentials)

    if (response?.access_token || response?.refresh_token) {
      setAuthTokens(response)
      const user = await getCurrentUser()
      return user
    }

    return response
  }

  const signUp = async (credentials) => gateway.signUp(credentials)

  return Object.freeze({
    requestPasswordReset: (credentials) => gateway.requestPasswordReset(credentials),
    signIn,
    signUp,
  })
}

const backendGateway = {
  requestPasswordReset: async () => {
    throw new AuthIntegrationUnavailableError()
  },
  signIn: async ({ email, password }) => {
    const { data } = await apiClient.post('/auth/login', { email, password })
    setAuthTokens(data)
    return data
  },
  signUp: async ({ email, password, fullName, role }) => {
    const { data } = await apiClient.post('/auth/register', {
      email,
      password,
      full_name: fullName,
      role: role || 'CANDIDATE',
    })
    return data
  },
}

export const authService = createAuthService(backendGateway)

export async function logoutClientSession() {
  const refreshToken = window.localStorage.getItem('skillsync.refresh_token')
  if (refreshToken) await apiClient.post('/auth/logout', { refresh_token: refreshToken })
  clearAuthTokens()
}

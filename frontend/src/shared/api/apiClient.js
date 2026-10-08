import axios from 'axios'

import { env } from '@/shared/config/env'

const ACCESS_TOKEN_STORAGE_KEY = 'skillsync.access_token'
const REFRESH_TOKEN_STORAGE_KEY = 'skillsync.refresh_token'

export function getAccessToken() {
  return typeof window === 'undefined' ? null : window.localStorage.getItem(ACCESS_TOKEN_STORAGE_KEY)
}

export function getRefreshToken() {
  return typeof window === 'undefined' ? null : window.localStorage.getItem(REFRESH_TOKEN_STORAGE_KEY)
}

export function setAuthTokens({ access_token, refresh_token }) {
  if (typeof window === 'undefined') {
    return
  }

  if (access_token) {
    window.localStorage.setItem(ACCESS_TOKEN_STORAGE_KEY, access_token)
  }

  if (refresh_token) {
    window.localStorage.setItem(REFRESH_TOKEN_STORAGE_KEY, refresh_token)
  }
}

export function clearAuthTokens() {
  if (typeof window === 'undefined') {
    return
  }

  window.localStorage.removeItem(ACCESS_TOKEN_STORAGE_KEY)
  window.localStorage.removeItem(REFRESH_TOKEN_STORAGE_KEY)
}

export const apiClient = axios.create({
  baseURL: env.apiBaseUrl || undefined,
  timeout: 60_000,
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  },
})

let refreshPromise = null

async function refreshAccessToken() {
  const refreshToken = getRefreshToken()
  if (!refreshToken) throw new Error('No refresh token')
  const baseUrl = env.apiBaseUrl || ''
  const { data } = await axios.post(`${baseUrl}/auth/refresh`, { refresh_token: refreshToken }, {
    timeout: 15_000,
    baseURL: undefined,
    headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
  })
  setAuthTokens(data)
  return data.access_token
}

apiClient.interceptors.request.use((config) => {
  const token = getAccessToken()

  if (token) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error?.response?.status !== 401) throw error
    const request = error.config || {}
    // /auth/me is a protected endpoint too: reload must refresh an expired session.
    const isCredentialRequest = /\/auth\/(login|register|refresh)(?:$|[/?])/.test(request.url || '')
    if (isCredentialRequest) throw error
    if (!request._retry && getRefreshToken()) {
      request._retry = true
      try {
        refreshPromise ||= refreshAccessToken().finally(() => { refreshPromise = null })
        const token = await refreshPromise
        request.headers = request.headers || {}
        request.headers.Authorization = `Bearer ${token}`
        if (/\/auth\/logout(?:$|[/?])/.test(request.url || '')) {
          request.data = JSON.stringify({ refresh_token: getRefreshToken() })
        }
      } catch {
        clearAuthTokens()
        if (typeof window !== 'undefined' && !window.location.pathname.startsWith('/login')) window.location.assign('/login')
        throw error
      }
      // Do not erase credentials if the retried operation fails for a non-auth reason.
      return apiClient.request(request)
    }
    clearAuthTokens()
    if (typeof window !== 'undefined' && !window.location.pathname.startsWith('/login')) window.location.assign('/login')
    throw error
  },
)

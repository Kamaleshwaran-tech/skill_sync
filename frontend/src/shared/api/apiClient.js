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
  timeout: 10_000,
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  },
})

let refreshPromise = null

async function refreshAccessToken() {
  const refreshToken = getRefreshToken()
  if (!refreshToken) throw new Error('No refresh token')
  const { data } = await axios.post(`${env.apiBaseUrl || ''}/auth/refresh`, { refresh_token: refreshToken }, {
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
  (error) => {
    if (error?.response?.status === 401) {
      const isAuthRequest = /\/auth\//.test(error.config?.url || '')
      if (!isAuthRequest && !error.config?._retry && getRefreshToken()) {
        error.config._retry = true
        refreshPromise ||= refreshAccessToken().finally(() => { refreshPromise = null })
        return refreshPromise.then((token) => {
          error.config.headers = error.config.headers || {}
          error.config.headers.Authorization = `Bearer ${token}`
          return apiClient.request(error.config)
        }).catch(() => {
          clearAuthTokens()
          throw error
        })
      }
      if (!isAuthRequest) {
        clearAuthTokens()
        if (typeof window !== 'undefined' && !window.location.pathname.startsWith('/login')) window.location.assign('/login')
      }
    }

    return Promise.reject(error)
  },
)

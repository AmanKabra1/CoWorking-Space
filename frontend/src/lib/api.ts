import axios, { type InternalAxiosRequestConfig } from 'axios'
import { useAuthStore } from '@/store/auth'

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

const api = axios.create({
  baseURL: `${BASE_URL}/api/v1`,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const { accessToken, user } = useAuthStore.getState()
  if (accessToken) config.headers.Authorization = `Bearer ${accessToken}`
  if (user?.company) config.headers['X-Company-ID'] = user.company
  return config
})

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      try {
        const refresh = useAuthStore.getState().refreshToken
        const { data } = await axios.post(`${BASE_URL}/api/v1/auth/token/refresh/`, {
          refresh,
        })
        // Backend rotates refresh tokens and blacklists the old one, so persist
        // the new refresh token when one is returned — reusing the old one fails.
        useAuthStore.getState().setTokens(data.access, data.refresh ?? refresh!)
        original.headers.Authorization = `Bearer ${data.access}`
        return api(original)
      } catch {
        useAuthStore.getState().logout()
        if (typeof window !== 'undefined') window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api

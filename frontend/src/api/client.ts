import axios from 'axios'

let csrfToken: string | undefined
let csrfRequest: Promise<string> | undefined

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'https://api.banxia.xin',
  withCredentials: true,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

export function clearCsrfToken(): void {
  csrfToken = undefined
  csrfRequest = undefined
}

async function getCsrfToken(): Promise<string> {
  if (csrfToken) return csrfToken
  if (!csrfRequest) {
    csrfRequest = api.get<{ csrf_token: string }>('/api/auth/csrf').then(response => {
      const token = response.data.csrf_token
      csrfToken = token
      return token
    }).finally(() => { csrfRequest = undefined })
  }
  return csrfRequest
}

api.interceptors.request.use(async config => {
  const method = config.method?.toUpperCase()
  if (method && !['GET', 'HEAD', 'OPTIONS'].includes(method)) {
    const token = await getCsrfToken()
    config.headers.set('X-CSRF-Token', token)
  }
  return config
})

api.interceptors.response.use(
  response => response,
  error => Promise.reject(new Error(error.response?.data?.detail || error.message || '请求失败，请稍后重试')),
)

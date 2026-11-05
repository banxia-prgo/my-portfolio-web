import axios from 'axios'

let csrfToken: string | undefined
let csrfRequest: Promise<string> | undefined

async function getCsrfToken(): Promise<string> {
  if (csrfToken) return csrfToken
  if (!csrfRequest) {
    csrfRequest = axios.get<{ csrf_token: string }>(
      (import.meta.env.VITE_API_BASE_URL || 'https://api.banxia.xin') + '/api/auth/csrf',
      { withCredentials: true, timeout: 15000 },
    ).then(response => {
      const token = response.data.csrf_token
      csrfToken = token
      return token
    }).finally(() => { csrfRequest = undefined })
  }
  return csrfRequest
}

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'https://api.banxia.xin',
  withCredentials: true,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

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

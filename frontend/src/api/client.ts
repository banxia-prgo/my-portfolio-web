import axios from 'axios'

function csrfCookie(): string | undefined {
  const match = document.cookie.match(/(?:^|; )bx_csrf=([^;]*)/)
  return match ? decodeURIComponent(match[1]) : undefined
}

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'https://api.banxia.xin',
  withCredentials: true,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use(config => {
  const method = config.method?.toUpperCase()
  if (method && !['GET', 'HEAD', 'OPTIONS'].includes(method)) {
    const token = csrfCookie()
    if (token) config.headers.set('X-CSRF-Token', token)
  }
  return config
})

api.interceptors.response.use(
  response => response,
  error => Promise.reject(new Error(error.response?.data?.detail || error.message || '请求失败，请稍后重试')),
)

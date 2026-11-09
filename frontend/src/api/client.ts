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

function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail: unknown = error.response?.data?.detail

    if (typeof detail === 'string') return detail

    if (Array.isArray(detail)) {
      return detail.map(item => {
        if (typeof item === 'string') return item
        if (item && typeof item === 'object') {
          const info = item as { loc?: unknown[]; msg?: unknown }
          const location = Array.isArray(info.loc) ? info.loc.join('.') : ''
          if (typeof info.msg === 'string') {
            return location ? `${location}: ${info.msg}` : info.msg
          }
        }
        try {
          return JSON.stringify(item) ?? String(item)
        } catch {
          return String(item)
        }
      }).join('；')
    }

    if (detail !== undefined && detail !== null) {
      if (typeof detail === 'object') {
        try {
          return JSON.stringify(detail) ?? error.message
        } catch {
          return error.message || '请求失败，请稍后重试'
        }
      }
      return String(detail)
    }

    return error.message || '请求失败，请稍后重试'
  }

  return error instanceof Error ? error.message : '请求失败，请稍后重试'
}

api.interceptors.request.use(async config => {
  // FormData must let the browser set multipart/form-data with its boundary.
  if (typeof FormData !== 'undefined' && config.data instanceof FormData) {
    config.headers.delete('Content-Type')
  }

  const method = config.method?.toUpperCase()
  if (method && !['GET', 'HEAD', 'OPTIONS'].includes(method)) {
    const token = await getCsrfToken()
    config.headers.set('X-CSRF-Token', token)
  }
  return config
})

api.interceptors.response.use(
  response => response,
  error => Promise.reject(new Error(getErrorMessage(error))),
)

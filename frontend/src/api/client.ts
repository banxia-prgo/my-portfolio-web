import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'https://api.banxia.xin',
  withCredentials: true,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.response.use(r => r, error => Promise.reject(new Error(error.response?.data?.detail || error.message || '请求失败')))

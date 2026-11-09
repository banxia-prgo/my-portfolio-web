import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/api/client'

export interface AuthUser {
  id: number
  email: string
  nickname: string
  avatar_url: string | null
  created_at: string
  role: 'user' | 'admin'
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<AuthUser | null>(null)
  const initialized = ref(false)
  let initialization: Promise<void> | null = null
  let revision = 0

  async function initialize(): Promise<void> {
    if (initialized.value) return
    if (initialization) return initialization

    const requestRevision = revision
    initialization = api.get<AuthUser>('/api/users/me')
      .then(response => {
        if (revision === requestRevision) user.value = response.data
      })
      .catch(() => {
        if (revision === requestRevision) user.value = null
      })
      .finally(() => {
        if (revision === requestRevision) initialized.value = true
        initialization = null
      })

    return initialization
  }

  function setUser(nextUser: AuthUser): void {
    revision += 1
    user.value = nextUser
    initialized.value = true
  }

  function clearUser(): void {
    revision += 1
    user.value = null
    initialized.value = true
  }

  return { user, initialized, initialize, setUser, clearUser }
})

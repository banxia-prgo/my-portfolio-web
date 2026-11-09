import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import ArchiveView from '@/views/ArchiveView.vue'
import ArticleView from '@/views/ArticleView.vue'
import ProjectsView from '@/views/ProjectsView.vue'
import AboutView from '@/views/AboutView.vue'
import GuestbookView from '@/views/GuestbookView.vue'
import AuthView from '@/views/AuthView.vue'
import ProfileView from '@/views/ProfileView.vue'
import NotFoundView from '@/views/NotFoundView.vue'
import { api } from '@/api/client'

const router = createRouter({
  history: createWebHistory(),
  scrollBehavior: () => ({ top: 0, behavior: 'smooth' }),
  routes: [
    { path: '/', component: HomeView },
    { path: '/posts/', component: ArchiveView },
    { path: '/posts/:slug/', component: ArticleView },
    { path: '/projects/', component: ProjectsView },
    { path: '/projects/:slug/', component: ArticleView },
    { path: '/guestbook/', component: GuestbookView },
    { path: '/about/', component: AboutView },
    // Keep old bookmarks and search-engine links working after removing the resume page.
    { path: '/resume/', redirect: '/about/' },
    { path: '/login/', component: AuthView, props: { mode: 'login' } },
    { path: '/register/', component: AuthView, props: { mode: 'register' } },
    { path: '/profile/', component: ProfileView, meta: { requiresAuth: true } },
    { path: '/:pathMatch(.*)*', component: NotFoundView },
  ],
})

router.beforeEach(async (to) => {
  if (to.meta.requiresAuth) {
    try {
      await api.get('/api/users/me')
    } catch {
      return { path: '/login/', query: { redirect: to.fullPath } }
    }
  }
})

export default router

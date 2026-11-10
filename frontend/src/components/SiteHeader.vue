<script setup lang="ts">
import { Menu, X, ArrowUpRight, UserRound, Leaf } from 'lucide-vue-next'
import { ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const open = ref(false)
const route = useRoute()
const auth = useAuthStore()
const links = [
  { label: '首页', to: '/' },
  { label: '文章', to: '/posts/' },
  { label: '项目', to: '/projects/' },
  { label: '留言', to: '/guestbook/' },
  { label: '关于我', to: '/about/' },
]
</script>

<template>
  <header class="header site-header">
    <div class="header-inner nav">
      <div class="logo">
        <RouterLink to="/" class="brand" @click="open = false">
          <Leaf class="brand-symbol" :size="23" :stroke-width="1.7" aria-hidden="true" />
          <span class="brand-wordmark">半夏小筑</span>
        </RouterLink>
      </div>
      <nav id="menu" class="desktop-nav" aria-label="主导航">
        <RouterLink v-for="link in links" :key="link.to" :to="link.to"
          :class="{ active: route.path === link.to || (link.to !== '/' && route.path.startsWith(link.to)) }">{{ link.label }}</RouterLink>
      </nav>
      <div class="header-actions">
        <RouterLink v-if="auth.user?.role === 'admin'" class="login-link" to="/admin/">管理后台</RouterLink>
        <RouterLink v-if="auth.user" class="login-link" to="/profile/" :aria-label="`个人中心：${auth.user.nickname}`"><UserRound :size="14"/> {{ auth.user.nickname }}</RouterLink>
        <RouterLink v-else-if="auth.initialized" class="login-link" to="/login/">登录 <ArrowUpRight :size="14"/></RouterLink>
        <span v-else class="login-link" aria-label="正在恢复登录状态" aria-live="polite">…</span>
        <button class="mobile-menu" :aria-label="open ? '关闭菜单' : '打开菜单'" @click="open = !open"><X v-if="open" :size="20"/><Menu v-else :size="20"/></button>
      </div>
    </div>
    <nav v-if="open" class="mobile-nav" aria-label="移动端导航">
      <RouterLink v-for="link in links" :key="link.to" :to="link.to" @click="open = false">{{ link.label }}</RouterLink>
      <RouterLink v-if="auth.user?.role === 'admin'" to="/admin/" @click="open = false">管理后台</RouterLink>
      <RouterLink v-if="auth.user" to="/profile/" @click="open = false">{{ auth.user.nickname }} · 个人中心</RouterLink>
      <RouterLink v-else-if="auth.initialized" to="/login/" @click="open = false">登录 / 注册</RouterLink>
    </nav>
  </header>
</template>

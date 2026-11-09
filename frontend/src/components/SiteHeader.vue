<script setup lang="ts">
import { Menu, X, ArrowUpRight } from 'lucide-vue-next'
import { ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

const open = ref(false)
const route = useRoute()
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
        <RouterLink to="/" class="brand" @click="open = false">半夏小筑</RouterLink>
      </div>
      <nav id="menu" class="desktop-nav" aria-label="主导航">
        <RouterLink
          v-for="link in links"
          :key="link.to"
          :to="link.to"
          :class="{ active: route.path === link.to || (link.to !== '/' && route.path.startsWith(link.to)) }"
        >{{ link.label }}</RouterLink>
      </nav>
      <div class="header-actions">
        <RouterLink class="login-link" to="/login/">登录 <ArrowUpRight :size="15" /></RouterLink>
        <button class="mobile-menu" :aria-label="open ? '关闭菜单' : '打开菜单'" @click="open = !open">
          <X v-if="open" :size="21" />
          <Menu v-else :size="21" />
        </button>
      </div>
    </div>
    <nav v-if="open" class="mobile-nav" aria-label="移动端导航">
      <RouterLink v-for="link in links" :key="link.to" :to="link.to" @click="open = false">{{ link.label }}</RouterLink>
      <RouterLink to="/login/" @click="open = false">登录 / 注册</RouterLink>
    </nav>
  </header>
</template>

<script setup lang="ts">
import { Menu, X, ArrowUpRight } from 'lucide-vue-next'
import { ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
const open = ref(false)
const route = useRoute()
const links = [
  { label: '首页', to: '/' },
  { label: '项目', to: '/projects/' },
  { label: '随笔', to: '/posts/' },
  { label: '简历', to: '/resume/' },
]
</script>

<template>
  <header class="site-header">
    <div class="header-inner">
      <RouterLink to="/" class="brand" @click="open = false">
        <span class="brand-mark">半</span>
        <span class="brand-copy"><strong>半夏小筑</strong><small>代码与思绪的栖居之所</small></span>
      </RouterLink>
      <nav class="desktop-nav" aria-label="主导航">
        <RouterLink v-for="link in links" :key="link.to" :to="link.to" :class="{ active: route.path === link.to || (link.to !== '/' && route.path.startsWith(link.to)) }">{{ link.label }}</RouterLink>
      </nav>
      <div class="header-actions">
        <RouterLink class="login-link" to="/login/">登录 <ArrowUpRight :size="15" /></RouterLink>
        <button class="mobile-menu" :aria-label="open ? '关闭菜单' : '打开菜单'" @click="open = !open"><X v-if="open" /><Menu v-else /></button>
      </div>
    </div>
    <nav v-if="open" class="mobile-nav">
      <RouterLink v-for="link in links" :key="link.to" :to="link.to" @click="open = false">{{ link.label }}</RouterLink>
      <RouterLink to="/login/" @click="open = false">登录 / 注册</RouterLink>
    </nav>
  </header>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { Leaf } from 'lucide-vue-next'
</script>
<template>
  <footer class="footer bx-site-footer">
    <div class="footer-inner bx-footer-inner">
      <nav class="bx-footer-nav" aria-label="页脚导航">
        <RouterLink to="/">首页</RouterLink>
        <RouterLink to="/posts/">文章</RouterLink>
        <RouterLink to="/projects/">项目</RouterLink>
        <RouterLink to="/guestbook/">留言</RouterLink>
        <RouterLink to="/about/">关于我</RouterLink>
      </nav>
      <RouterLink to="/" class="bx-footer-brand">
        <span class="bx-footer-brand__wordmark">
          <Leaf class="bx-footer-brand__leaf" :size="22" :stroke-width="1.7" aria-hidden="true" />
          <strong>半夏小筑</strong>
        </span>
        <small>代码与思绪的栖居之所</small>
      </RouterLink>
      <div class="bx-footer-meta">
        <span>© 2026 Banxia</span>
        <span>Built with curiosity &amp; care</span>
        <a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener noreferrer">陕ICP备2026032591号-1</a>
      </div>
    </div>
  </footer>
</template>

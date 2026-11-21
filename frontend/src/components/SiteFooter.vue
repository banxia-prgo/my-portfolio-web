<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { Leaf } from 'lucide-vue-next'
</script>
<template>
  <footer class="footer bx-site-footer">
    <div class="footer-inner bx-footer-inner">
      <div class="bx-footer-meta__filings" aria-label="网站备案信息">
        <a href="https://beian.mps.gov.cn/#/query/webSearch?code=61019002004464" target="_blank" rel="noopener noreferrer">陕公网安备61019002004464号</a>
        <a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener noreferrer">陕ICP备2026032591号-1</a>
      </div>
      <RouterLink to="/" class="bx-footer-brand">
        <span class="bx-footer-brand__wordmark">
          <Leaf class="bx-footer-brand__leaf" :size="22" :stroke-width="1.7" aria-hidden="true" />
          <strong>半夏小筑</strong>
        </span>
      </RouterLink>
      <div class="bx-footer-meta__copyright">
        <span>© 2026 Banxia</span>
        <span>Built with curiosity &amp; care</span>
      </div>
    </div>
  </footer>
</template>

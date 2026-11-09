<template>
  <footer class="footer">
    <div class="footer-inner">
      <div>
        <span class="footer-mark">半夏小筑</span>
        <p>代码与思绪的栖居之所</p>
      </div>
      <div class="footer-meta">
        <span>© {{ new Date().getFullYear() }} Banxia</span>
        <span>Built with curiosity &amp; care</span>
        <a
          class="filing-link"
          href="https://beian.miit.gov.cn/"
          target="_blank"
          rel="noopener noreferrer"
        >陕ICP备2026032591号-1</a>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.filing-link {
  color: inherit;
  font-size: 0.8rem;
  opacity: 0.72;
  text-decoration: none;
  transition: opacity 0.2s ease;
}

.filing-link:hover {
  opacity: 1;
}
</style>

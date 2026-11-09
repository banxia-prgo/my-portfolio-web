<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <article class="about-page post-single">
    <nav class="post-breadcrumb" aria-label="面包屑"><RouterLink to="/">首页</RouterLink><span>/</span><span>关于我</span></nav>
    <header class="post-header">
      <p class="post-meta">ABOUT / BANXIA</p>
      <h1>关于半夏</h1>
      <p class="post-description">以代码记录成长，以思考探索世界。在技术与生活之间，保持好奇，持续前行。</p>
    </header>

    <section class="about-profile">
      <div class="about-avatar">半</div>
      <div class="about-profile__copy">
        <p class="about-kicker">NICE TO MEET YOU</p>
        <h2>你好，我是半夏。</h2>
        <p>一名热爱技术、喜欢动手实践的开发者。</p>
        <div class="about-links">
          <a href="https://github.com/banxia-prgo" target="_blank" rel="noopener noreferrer">GitHub ↗</a>
          <a href="mailto:dhq1015@gmail.com">dhq1015@gmail.com</a>
        </div>
      </div>
    </section>

    <section class="about-section">
      <p class="about-kicker">WHAT I'M EXPLORING</p>
      <h2>持续探索的方向</h2>
      <div class="about-focus-grid">
        <article><span>01 / VISION</span><h3>机器视觉</h3><p>围绕 OpenCV、图像处理、目标检测与工业视觉应用，积累可运行、可复现的实践经验。</p><div>OpenCV · C++ · Qt</div></article>
        <article><span>02 / AI</span><h3>深度学习</h3><p>学习神经网络、图像分类与目标检测，尝试从数据准备、模型训练走向实际应用。</p><div>Python · PyTorch · YOLO</div></article>
        <article><span>03 / ENGINEERING</span><h3>工程实践</h3><p>关注软件架构、开发工具链、Linux 环境与项目部署，让想法成为稳定可用的作品。</p><div>Git · Linux · Docker</div></article>
      </div>
    </section>

    <section class="about-section about-principle">
      <p class="about-kicker">A LITTLE NOTE</p>
      <h2>关于这里</h2>
      <p>「半夏小筑」是我的个人数字空间。这里记录技术学习中的问题与解法，收纳亲手完成的项目，也留下一些关于成长和生活的思考。</p>
      <p>如果你对某篇文章或某个项目有想法，欢迎到留言板交流。</p>
      <RouterLink class="about-guestbook-link" to="/guestbook/">去留言板聊聊 <span>→</span></RouterLink>
    </section>
  </article>
</template>

<style scoped>
.about-page{max-width:980px}.about-profile{display:flex;align-items:center;gap:28px;margin:0 0 3rem;padding:28px;border:1px solid var(--border);border-radius:22px;background:linear-gradient(120deg,#f6f3ff 0%,#f2fbfa 100%)}.about-avatar{flex:0 0 104px;width:104px;height:104px;display:grid;place-items:center;border:6px solid #fff;border-radius:34px;background:linear-gradient(145deg,#c9c0f5,#b9e7e1);color:#6254a5;font-family:serif;font-size:48px;box-shadow:0 12px 30px #8170cc20}.about-kicker{margin:0 0 10px;color:#8170cc;font-size:10px;font-weight:800;letter-spacing:.18em}.about-profile h2,.about-section h2{margin:0 0 10px;color:var(--primary);font-size:clamp(1.5rem,3vw,2rem)}.about-profile__copy>p:not(.about-kicker){color:var(--secondary);font-size:.9rem}.about-links{display:flex;flex-wrap:wrap;gap:18px;margin-top:18px}.about-links a,.about-guestbook-link{color:#7668c4;font-size:.8rem;font-weight:700}.about-section{margin:3.5rem 0}.about-focus-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin-top:1.5rem}.about-focus-grid article{padding:22px;border:1px solid var(--border);border-radius:17px;background:var(--entry)}.about-focus-grid article>span{color:#8b7dd0;font-size:9px;letter-spacing:.14em}.about-focus-grid h3{margin:15px 0 8px;font-size:1.1rem}.about-focus-grid p,.about-principle>p:not(.about-kicker){color:var(--secondary);font-size:.84rem;line-height:1.9}.about-focus-grid article>div{margin-top:15px;padding-top:12px;border-top:1px solid var(--border);color:#8274c6;font-size:.7rem}.about-principle{max-width:760px}.about-guestbook-link{display:inline-flex;gap:12px;margin-top:12px;padding:11px 16px;border:1px solid #dcd5f3;border-radius:999px;background:#f7f5ff}@media(max-width:700px){.about-profile{align-items:flex-start;flex-direction:column;padding:22px}.about-focus-grid{grid-template-columns:1fr}.about-section{margin:2.5rem 0}}
</style>

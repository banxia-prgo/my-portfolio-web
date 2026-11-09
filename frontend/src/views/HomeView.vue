<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { loadCatalog, type ArticleContent } from '@/api/content'

const projects = ref<ArticleContent[]>([])
const posts = ref<ArticleContent[]>([])
const projectCount = ref(0)
const postCount = ref(0)
const featuredProject = computed(() => projects.value[0])

onMounted(async () => {
  try {
    const data = await loadCatalog()
    projectCount.value = data.projects.length
    postCount.value = data.posts.length
    projects.value = data.projects.slice(0, 1)
    posts.value = data.posts.slice(0, 2)
  } catch (error) {
    console.error('加载首页内容失败', error)
  }
})
</script>

<template>
  <div class="home-page">
    <section class="bx-home-hero" aria-labelledby="bx-home-title">
      <div class="bx-home-hero__copy">
        <p class="bx-eyebrow">HELLO, I'M BANXIA</p>
        <h1 id="bx-home-title">半夏小筑</h1>
        <p class="bx-home-hero__subtitle"><span></span>代码与思绪的栖居之所</p>
        <p class="bx-home-hero__desc">
          热爱技术，专注于计算机视觉、深度学习与工程实践，<br>
          在代码与思考中，记录成长，分享思绪。
        </p>
        <div class="bx-home-hero__actions">
          <RouterLink class="bx-btn bx-btn--primary" to="/projects/">♧ 查看我的项目 <span>→</span></RouterLink>
          <RouterLink class="bx-btn bx-btn--ghost" to="/posts/">▣ 阅读文章</RouterLink>
        </div>
      </div>
      <div class="bx-home-hero__poem">在代码构筑的世界里<br>遇见更好的自己<br><span>— 半夏</span></div>
    </section>

    <section class="bx-tech-strip" aria-label="技术方向">
      <div class="bx-tech-strip__label"><span>‹/›</span> 技术方向</div>
      <div class="bx-tech-strip__items">
        <span class="bx-pill bx-pill--purple">◉ C++</span>
        <span class="bx-pill bx-pill--blue">◉ Python</span>
        <span class="bx-pill bx-pill--purple">◉ OpenCV</span>
        <span class="bx-pill bx-pill--purple">◉ 深度学习</span>
        <span class="bx-pill bx-pill--aqua">◉ 机器视觉</span>
        <span class="bx-pill bx-pill--aqua">◉ Linux</span>
        <span class="bx-pill bx-pill--purple">◉ Git</span>
        <span class="bx-pill bx-pill--aqua">◉ Docker</span>
        <span class="bx-pill bx-pill--blue">◉ Web 开发</span>
      </div>
      <span class="bx-tech-strip__next">›</span>
    </section>

    <div class="bx-home-content">
      <div class="bx-home-main">
        <section class="bx-section bx-projects" aria-labelledby="bx-projects-title">
          <div class="bx-section__head">
            <h2 id="bx-projects-title"><span>☆</span> 精选项目</h2>
            <RouterLink to="/projects/">查看全部 →</RouterLink>
          </div>
          <div class="bx-project-grid">
            <article v-if="featuredProject" class="bx-project-card">
              <RouterLink class="bx-project-card__visual bx-project-card__visual--browser" :to="featuredProject.href">
                <div class="bx-browser-mock">
                  <div class="bx-browser-mock__bar"><i></i><i></i><i></i><span>图片浏览器</span></div>
                  <div class="bx-browser-mock__body">
                    <div class="bx-browser-mock__side"></div>
                    <div class="bx-browser-mock__tiles"><i></i><i></i><i></i><i></i><i></i><i></i></div>
                    <div class="bx-browser-mock__preview"></div>
                  </div>
                </div>
              </RouterLink>
              <div class="bx-project-card__body">
                <h3><RouterLink :to="featuredProject.href">{{ featuredProject.title }}</RouterLink><span class="bx-tag-hot">推荐</span></h3>
                <p>{{ featuredProject.summary }}</p>
                <div class="bx-project-tags"><span>C++</span><span>Qt</span><span>图像处理</span></div>
                <div class="bx-project-card__foot">
                  <a href="https://github.com/banxia-prgo/picture_browser" target="_blank" rel="noopener">◉ GitHub</a>
                  <RouterLink :to="featuredProject.href">项目详情 →</RouterLink>
                </div>
              </div>
            </article>
            <article v-else class="bx-project-card">
              <div class="bx-project-card__visual bx-project-card__visual--browser">
                <div class="bx-browser-mock"><div class="bx-browser-mock__bar"><i></i><i></i><i></i><span>图片浏览器</span></div><div class="bx-browser-mock__body"><div class="bx-browser-mock__side"></div><div class="bx-browser-mock__tiles"><i></i><i></i><i></i><i></i><i></i><i></i></div><div class="bx-browser-mock__preview"></div></div></div>
              </div>
              <div class="bx-project-card__body"><h3>图片浏览器 <span class="bx-tag-hot">项目</span></h3><p>基于 C++ 和 Qt 的本地图片浏览工具。</p><div class="bx-project-tags"><span>C++</span><span>Qt</span><span>图像处理</span></div></div>
            </article>

            <article class="bx-project-card">
              <div class="bx-project-card__visual bx-project-card__visual--vision">
                <div class="bx-vision-scene"><span class="bx-vision-car"></span><i></i><b></b><em></em><small>VISION / STUDY</small></div>
              </div>
              <div class="bx-project-card__body">
                <h3>机器视觉学习 <span class="bx-tag-study">学习中</span></h3>
                <p>从 OpenCV 的目标检测与图像处理基础出发，逐步搭建可复现的视觉实验。</p>
                <div class="bx-project-tags"><span>Python</span><span>OpenCV</span><span>YOLO</span></div>
                <div class="bx-project-card__foot"><span>学习方向</span><RouterLink to="/about/">学习方向 →</RouterLink></div>
              </div>
            </article>

            <article class="bx-project-card">
              <div class="bx-project-card__visual bx-project-card__visual--learning">
                <div class="bx-neural-art"><span></span><i></i><b></b><em></em><small>DEEP LEARNING</small></div>
              </div>
              <div class="bx-project-card__body">
                <h3>深度学习实践 <span class="bx-tag-study">学习中</span></h3>
                <p>基于 PyTorch 学习图像分类、模型训练与可视化，积累从实验到部署的经验。</p>
                <div class="bx-project-tags"><span>Python</span><span>PyTorch</span><span>深度学习</span></div>
                <div class="bx-project-card__foot"><span>学习方向</span><RouterLink to="/posts/">学习笔记 →</RouterLink></div>
              </div>
            </article>
          </div>
        </section>

        <section class="bx-section bx-notes" aria-labelledby="bx-notes-title">
          <div class="bx-section__head">
            <h2 id="bx-notes-title"><span>✎</span> 最新文章</h2>
            <RouterLink to="/posts/">查看全部 →</RouterLink>
          </div>
          <div class="bx-note-list">
            <RouterLink v-for="post in posts" :key="post.slug" class="bx-note" :to="post.href">
              <span class="bx-note__thumb" :class="post.slug.includes('linux') ? 'bx-note__thumb--mountain' : 'bx-note__thumb--code'"><i></i><b></b></span>
              <span class="bx-note__content">
                <strong>{{ post.title }}</strong>
                <span>{{ post.summary }}</span>
                <small>▣ {{ post.date?.slice(0, 10) }}　·　{{ (post.tags || []).join(' · ') }}　·　阅读笔记</small>
              </span>
              <span class="bx-note__arrow">→</span>
            </RouterLink>
            <p v-if="!posts.length" class="bx-empty">文章正在整理中。</p>
          </div>
        </section>
      </div>

      <aside class="bx-home-sidebar">
        <section class="bx-about-card">
          <div class="bx-about-card__leaf">❧</div>
          <div class="bx-about-card__heading"><span class="bx-avatar">半</span><div><h2>关于我</h2><p>一名热爱技术的开发者</p></div></div>
          <p class="bx-about-card__intro">目前专注于计算机视觉、深度学习和工程实践，持续学习，记录成长。</p>
          <div class="bx-about-item"><span>♧</span><div><strong>学习方向</strong><p>机器视觉 · 深度学习 · 工程落地</p></div></div>
          <div class="bx-about-item"><span>♧</span><div><strong>联系方式</strong><p><a href="mailto:dhq1015@gmail.com">dhq1015@gmail.com</a></p></div></div>
          <RouterLink class="bx-about-link" to="/about/">了解更多关于我 →</RouterLink>
        </section>

        <section class="bx-learning-card">
          <div class="bx-section__head"><h2><span>◎</span> 我的学习方向</h2><RouterLink to="/about/">更多内容 →</RouterLink></div>
          <div class="bx-learning-step"><span>01</span><div><strong>机器视觉</strong><p>OpenCV · 图像处理 · 目标检测</p></div><small>进行中</small></div>
          <div class="bx-learning-step"><span>02</span><div><strong>深度学习</strong><p>PyTorch · 模型训练 · 项目实践</p></div></div>
          <div class="bx-learning-step"><span>03</span><div><strong>工程实践</strong><p>系统设计 · 项目部署 · 代码规范</p></div></div>
        </section>

        <section class="bx-stats-card">
          <div class="bx-section__head"><h2><span>▥</span> 数据一览</h2></div>
          <div class="bx-stats-grid">
            <RouterLink to="/posts/"><strong>✎　{{ postCount }}</strong><span>文章</span></RouterLink>
            <RouterLink to="/projects/"><strong>‹/›　{{ projectCount }}</strong><span>开源项目</span></RouterLink>
            <div><strong>♧　3</strong><span>学习方向</span></div>
            <div><strong>∞</strong><span>持续成长</span></div>
          </div>
          <blockquote>“ 永远保持学习的热情<br>让技术为生活创造更多可能 ”</blockquote>
        </section>
      </aside>
    </div>
  </div>
</template>

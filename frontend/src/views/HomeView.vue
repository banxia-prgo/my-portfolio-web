<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { ArrowRight, BarChart3, BookOpen, Code2, GraduationCap, Mail, NotebookPen, Sparkles, Target } from 'lucide-vue-next'
import { loadCatalog, type ArticleContent } from '@/api/content'

const projects = ref<ArticleContent[]>([])
const posts = ref<ArticleContent[]>([])
const projectCount = ref(0)
const postCount = ref(0)
const featuredProject = computed(() => projects.value[0])

function newestFirst(items: ArticleContent[]) {
  return [...items].sort((a, b) => (Date.parse(b.date || '') || 0) - (Date.parse(a.date || '') || 0))
}

onMounted(async () => {
  try {
    const catalog = await loadCatalog()
    projectCount.value = catalog.projects.length
    postCount.value = catalog.posts.length
    projects.value = newestFirst(catalog.projects).slice(0, 1)
    posts.value = newestFirst(catalog.posts).slice(0, 2)
  } catch (error) {
    console.error('加载首页内容失败', error)
  }
})
</script>

<template>
  <div class="home-page bx-home">
    <section class="bx-home-hero" aria-labelledby="bx-home-title">
      <div class="bx-home-hero__inner">
        <div class="bx-home-hero__copy">
          <p class="bx-eyebrow">HELLO, I'M BANXIA</p>
          <h1 id="bx-home-title">半夏小筑</h1>
          <p class="bx-home-hero__subtitle"><span></span>代码与思绪的栖居之所</p>
          <p class="bx-home-hero__desc">热爱技术，专注于计算机视觉、深度学习与工程实践，<br>在代码与思考中，记录成长、分享思绪。</p>
          <div class="bx-home-hero__actions">
            <RouterLink class="bx-btn bx-btn--primary" to="/projects/"><Code2 :size="14"/> 查看我的项目 <ArrowRight :size="14"/></RouterLink>
            <RouterLink class="bx-btn bx-btn--ghost" to="/posts/"><NotebookPen :size="14"/> 阅读随笔</RouterLink>
          </div>
        </div>
        <p class="bx-home-hero__poem">在代码构筑的世界里<br>遇见更好的自己<br><span>— 半夏</span></p>
      </div>
    </section>

    <section class="bx-tech-strip" aria-label="技术方向">
      <div class="bx-tech-strip__label"><Code2 :size="18"/> 技术方向</div>
      <div class="bx-tech-strip__items">
        <span class="bx-pill bx-pill--purple">✿ C++</span>
        <span class="bx-pill bx-pill--blue">✿ Python</span>
        <span class="bx-pill bx-pill--purple">✿ OpenCV</span>
        <span class="bx-pill bx-pill--purple">✿ 深度学习</span>
        <span class="bx-pill bx-pill--aqua">✿ 机器视觉</span>
        <span class="bx-pill bx-pill--aqua">✿ Linux</span>
        <span class="bx-pill bx-pill--purple">✿ Git</span>
        <span class="bx-pill bx-pill--aqua">✿ Docker</span>
        <span class="bx-pill bx-pill--blue">✿ Web开发</span>
      </div>
      <span class="bx-tech-strip__next" aria-hidden="true">›</span>
    </section>

    <div class="bx-home-grid">
      <section class="bx-section bx-projects" aria-labelledby="bx-projects-title">
        <div class="bx-section__head">
          <h2 id="bx-projects-title"><span class="bx-heading-icon">☆</span> 精选项目</h2>
          <RouterLink to="/projects/">查看全部 <ArrowRight :size="13"/></RouterLink>
        </div>
        <div class="bx-project-grid">
          <article class="bx-project-card">
            <RouterLink class="bx-project-card__visual" :to="featuredProject?.href || '/projects/'">
              <img src="/images/project-gallery.webp" alt="图片浏览器界面预览">
              <span class="bx-project-card__visual-label">BANXIA / IMAGE BROWSER</span>
            </RouterLink>
            <div class="bx-project-card__body">
              <h3><RouterLink :to="featuredProject?.href || '/projects/'">{{ featuredProject?.title || '图片浏览器' }}</RouterLink><span class="bx-tag-hot">精选</span></h3>
              <p>{{ featuredProject?.summary || '基于 C++ 和 Qt 的本地图片浏览工具，支持多格式预览与图像管理。' }}</p>
              <div class="bx-project-tags"><span>C++</span><span>Qt</span><span>图像处理</span></div>
              <div class="bx-project-card__foot">
                <a :href="featuredProject?.github || 'https://github.com/banxia-prgo/picture_browser'" target="_blank" rel="noopener noreferrer"><Code2 :size="13"/> GitHub</a>
                <RouterLink :to="featuredProject?.href || '/projects/'">项目详情 <ArrowRight :size="13"/></RouterLink>
              </div>
            </div>
          </article>

          <article class="bx-project-card">
            <RouterLink class="bx-project-card__visual bx-project-card__visual--vision" to="/about/">
              <img src="/images/project-vision.webp" alt="机器视觉目标检测项目预览">
            </RouterLink>
            <div class="bx-project-card__body">
              <h3><RouterLink to="/about/">机器视觉项目</RouterLink></h3>
              <p>基于 OpenCV 的目标检测与图像处理系统，实现多种视觉任务的应用。</p>
              <div class="bx-project-tags"><span>Python</span><span>OpenCV</span><span>YOLO</span></div>
              <div class="bx-project-card__foot"><span>学习实践</span><RouterLink to="/about/">项目详情 <ArrowRight :size="13"/></RouterLink></div>
            </div>
          </article>

          <article class="bx-project-card">
            <RouterLink class="bx-project-card__visual bx-project-card__visual--learning" to="/posts/">
              <img src="/images/project-ai.webp" alt="深度学习项目预览">
            </RouterLink>
            <div class="bx-project-card__body">
              <h3><RouterLink to="/posts/">深度学习项目</RouterLink></h3>
              <p>基于 PyTorch 的图像分类模型，包含数据处理、模型训练与可视化。</p>
              <div class="bx-project-tags"><span>Python</span><span>PyTorch</span><span>深度学习</span></div>
              <div class="bx-project-card__foot"><span>学习实践</span><RouterLink to="/posts/">学习笔记 <ArrowRight :size="13"/></RouterLink></div>
            </div>
          </article>
        </div>
      </section>

      <aside class="bx-about-card">
        <div class="bx-about-card__leaf" aria-hidden="true">❧</div>
        <div class="bx-about-card__heading"><span class="bx-avatar">半</span><div><h2>关于我</h2><p>一名热爱技术的开发者</p></div></div>
        <p class="bx-about-card__intro">目前专注于计算机视觉、深度学习和工程实践，持续学习，记录成长。</p>
        <div class="bx-about-item"><Mail :size="18"/><div><strong>联系邮箱</strong><p><a href="mailto:dhq1015@gmail.com">dhq1015@gmail.com</a></p></div></div>
        <div class="bx-about-item"><GraduationCap :size="19"/><div><strong>学习方向</strong><p>机器视觉 · 深度学习 · 工程落地</p></div></div>
        <RouterLink class="bx-about-link" to="/about/">了解更多关于我 <ArrowRight :size="14"/></RouterLink>
      </aside>

      <section class="bx-section bx-notes" aria-labelledby="bx-notes-title">
        <div class="bx-section__head">
          <h2 id="bx-notes-title"><span class="bx-heading-icon">✎</span> 最新文章</h2>
          <RouterLink to="/posts/">查看全部 <ArrowRight :size="13"/></RouterLink>
        </div>
        <div class="bx-note-list">
          <RouterLink v-for="(post, index) in posts" :key="post.slug" class="bx-note" :to="post.href">
            <span class="bx-note__thumb"><img :src="post.slug.includes('linux') ? '/images/post-linux.webp' : '/images/post-cpp.webp'" :alt="post.title"><span>{{ index + 1 }}</span></span>
            <span class="bx-note__content">
              <strong>{{ post.title }}</strong>
              <span>{{ post.summary }}</span>
              <small><BookOpen :size="11"/> {{ post.date?.slice(0, 10) }}　·　{{ (post.tags || []).slice(0, 1).join('') }}　·　阅读笔记</small>
            </span>
            <ArrowRight class="bx-note__arrow" :size="14"/>
          </RouterLink>
          <p v-if="!posts.length" class="bx-empty">文章正在整理中。</p>
        </div>
      </section>

      <section class="bx-learning-card">
        <div class="bx-section__head"><h2><Target :size="17"/> 我的学习方向</h2><RouterLink to="/about/">更多内容 <ArrowRight :size="13"/></RouterLink></div>
        <div class="bx-learning-step"><span>01</span><div><strong>机器视觉</strong><p>OpenCV · 图像处理 · 目标检测</p></div><small>进行中</small></div>
        <div class="bx-learning-step"><span>02</span><div><strong>深度学习</strong><p>PyTorch · 模型训练 · 项目实践</p></div></div>
        <div class="bx-learning-step"><span>03</span><div><strong>工程实践</strong><p>系统设计 · 项目部署 · 代码规范</p></div></div>
        <Sparkles class="bx-learning-decoration" :size="58"/>
      </section>

      <section class="bx-stats-card">
        <div class="bx-section__head"><h2><BarChart3 :size="17"/> 数据一览</h2></div>
        <div class="bx-stats-grid">
          <RouterLink to="/posts/"><strong><NotebookPen :size="17"/> {{ postCount }}</strong><span>原创随笔</span></RouterLink>
          <RouterLink to="/projects/"><strong><Code2 :size="18"/> {{ projectCount }}</strong><span>开源项目</span></RouterLink>
          <RouterLink to="/about/"><strong><BookOpen :size="17"/> 3</strong><span>学习方向</span></RouterLink>
          <div><strong><Sparkles :size="17"/> ∞</strong><span>持续成长</span></div>
        </div>
        <blockquote>“ 永远保持学习的热情<br>让技术为生活创造更多可能 ”</blockquote>
        <span class="bx-stats-leaf" aria-hidden="true">❧</span>
      </section>
    </div>
  </div>
</template>

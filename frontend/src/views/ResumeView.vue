<script setup lang="ts">
import { onMounted, ref } from 'vue'
import MarkdownIt from 'markdown-it'

interface ResumeSection { meta: Record<string, unknown>; content: string }
const sections = ref<ResumeSection[]>([])
const markdown = new MarkdownIt({ html: false, linkify: true, typographer: true })

onMounted(async () => {
  try {
    const response = await fetch('/content/resume.json')
    if (response.ok) sections.value = await response.json() as ResumeSection[]
  } catch {
    // Resume content is optional until the content migration script has run.
  }
})
</script>

<template>
  <article class="post-single resume-page">
    <nav class="post-breadcrumb" aria-label="面包屑"><RouterLink to="/">首页</RouterLink><span>/</span><span>简历</span></nav>
    <header class="post-header">
      <p class="post-meta">ABOUT / PROFILE</p>
      <h1>关于半夏</h1>
      <p class="post-description">专注于工业软件、机器视觉与深度学习方向的持续学习和实践。</p>
    </header>
    <div class="resume-intro">
      <span class="resume-avatar">半</span>
      <div><h2>半夏</h2><p>代码与思绪的栖居之所</p><a href="https://github.com/banxia-prgo" target="_blank" rel="noopener noreferrer">GitHub ↗</a></div>
    </div>
    <section class="post-content resume-content">
      <h2>学习方向</h2>
      <p>计算机视觉 · 深度学习 · C++ / Python · 工业上位机开发</p>
      <h2>技术栈</h2>
      <p class="resume-tags"><span>C++</span><span>Python</span><span>OpenCV</span><span>Qt / QML</span><span>PyTorch</span><span>FastAPI</span><span>Vue 3</span></p>
      <section v-for="(section, index) in sections" :key="index" class="resume-section">
        <h2>{{ String(section.meta.title || '简历资料') }}</h2>
        <div v-html="markdown.render(section.content)"></div>
      </section>
      <p v-if="!sections.length" class="resume-note">原有简历资料正在迁移整理中。</p>
    </section>
  </article>
</template>

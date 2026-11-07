<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { loadCatalog, type ArticleContent } from '@/api/content'

const query = ref('')
const projects = ref<ArticleContent[]>([])

onMounted(async () => {
  try {
    projects.value = (await loadCatalog()).projects
  } catch (error) {
    console.error('加载项目列表失败', error)
  }
})

const filtered = computed(() => {
  const q = query.value.trim().toLocaleLowerCase()
  return projects.value.filter(project =>
    [project.title, project.summary, ...(project.tags || [])].join(' ').toLocaleLowerCase().includes(q)
  )
})
</script>

<template>
  <div class="project-archive">
    <header class="project-archive__header">
      <p class="banxia-kicker">SELECTED WORK / EXPERIMENTS</p>
      <h1>项目作品</h1>
      <p class="project-archive__intro">把学习与想法做成可以运行、可以复现的项目。<br>记录目标、设计、实现与复盘。</p>
      <div class="project-archive__meta">
        <span>{{ projects.length }} 个项目</span>
        <span>持续更新 · 记录实践</span>
      </div>
    </header>

    <div class="project-toolbar">
      <label class="project-search">
        <span aria-hidden="true">⌕</span>
        <input v-model="query" type="search" placeholder="搜索项目名称或技术栈">
      </label>
    </div>

    <section class="project-archive__grid" aria-label="项目列表">
      <article v-for="(project, index) in filtered" :key="project.slug" class="project-archive-card">
        <RouterLink class="project-archive-card__media" :to="project.href">
          <img v-if="project.cover" :src="project.cover" :alt="project.title">
          <div v-else class="project-archive-card__placeholder">
            <span>PROJECT / {{ String(index + 1).padStart(2, '0') }}</span>
            <b>{{ project.title }}</b>
            <i>BANXIA STUDIO</i>
          </div>
          <span v-if="project.featured" class="project-archive-card__featured">精选项目</span>
        </RouterLink>
        <div class="project-archive-card__body">
          <div class="project-archive-card__eyebrow">
            <time>{{ project.date?.slice(0, 10) }}</time>
            <span>{{ (project.tags || []).join(' · ') || '开发实践' }}</span>
          </div>
          <h2><RouterLink :to="project.href">{{ project.title }}</RouterLink></h2>
          <p class="project-archive-card__summary">{{ project.summary }}</p>
          <div class="project-archive-card__links">
            <RouterLink :to="project.href">查看项目详情 ↗</RouterLink>
            <a v-if="project.slug === '图片浏览器'" href="https://github.com/banxia-prgo/picture_browser" target="_blank" rel="noopener">GitHub 源码 ↗</a>
          </div>
        </div>
      </article>
      <div v-if="!filtered.length" class="archive-empty">暂时没有匹配的项目。</div>
    </section>
  </div>
</template>

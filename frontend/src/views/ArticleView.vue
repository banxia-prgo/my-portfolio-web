<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import MarkdownIt from 'markdown-it'
import { loadCatalog, type ArticleContent } from '@/api/content'
import { api } from '@/api/client'

const route = useRoute()
const kind = route.path.startsWith('/projects/') ? 'project' : 'post'
const entry = ref<ArticleContent | null>(null)
const liked = ref(false)
const saved = ref(false)
const comment = ref('')
const notice = ref('')
const comments = ref<Array<{ id: number; content: string; nickname: string; created_at: string }>>([])
const markdown = new MarkdownIt({ html: false, linkify: true, typographer: true, breaks: false })

const slugify = (value: string) => value.trim().toLocaleLowerCase()
  .replace(/[\s]+/g, '-')
  .replace(/[，。！？、：；“”‘’（）【】《》]/g, '')
  .replace(/[^\u3400-\u9fff\w-]/g, '')
const headings = computed(() => {
  if (!entry.value) return []
  return markdown.parse(entry.value.content || '', {}).filter(token => token.type === 'heading_open').map((token, index) => {
    const inline = markdown.parse(entry.value!.content || '', {}).filter(item => item.type === 'inline')
    const text = inline[index]?.content || ''
    return { level: Number(token.tag.slice(1)), text, id: slugify(text) || `section-${index + 1}` }
  })
})
const rendered = computed(() => {
  if (!entry.value) return ''
  const tokens = markdown.parse(entry.value.content || '', {})
  let headingIndex = 0
  const renderer = new MarkdownIt({ html: false, linkify: true, typographer: true })
  renderer.renderer.rules.heading_open = (tokens, idx, options, env, self) => {
    const heading = headings.value[headingIndex++]
    if (heading) tokens[idx].attrSet('id', heading.id)
    return self.renderToken(tokens, idx, options)
  }
  return renderer.render(entry.value.content || '')
})

onMounted(async () => {
  const data = await loadCatalog()
  const list = kind === 'project' ? data.projects : data.posts
  entry.value = list.find(item => item.slug === String(route.params.slug)) || null
  if (kind === 'post') {
    try {
      const response = await api.get('/api/articles/' + String(route.params.slug) + '/comments')
      comments.value = response.data
    } catch {
      // The comments endpoint may not be available in the local API yet.
    }
  }
})

async function action(type: 'likes' | 'bookmarks') {
  try {
    const response = await api.post('/api/articles/' + String(route.params.slug) + '/' + type)
    if (type === 'likes') liked.value = response.data.active
    else saved.value = response.data.active
  } catch {
    notice.value = '请先登录，或稍后重试。'
  }
}

async function submit() {
  if (!comment.value.trim()) return
  try {
    await api.post('/api/comments', { article_slug: route.params.slug, content: comment.value })
    comment.value = ''
    notice.value = '评论已提交'
    const response = await api.get('/api/articles/' + String(route.params.slug) + '/comments')
    comments.value = response.data
  } catch {
    notice.value = '请先登录后发表评论。'
  }
}
</script>

<template>
  <article v-if="entry" :class="['post-single', kind === 'project' ? 'project-detail' : '']">
    <nav class="post-breadcrumb" aria-label="面包屑">
      <RouterLink to="/">首页</RouterLink><span>/</span>
      <RouterLink :to="kind === 'project' ? '/projects/' : '/posts/'">{{ kind === 'project' ? '项目' : '随笔' }}</RouterLink><span>/</span>
      <span>{{ entry.title }}</span>
    </nav>

    <header class="post-header" :class="{ 'project-detail__header': kind === 'project' }">
      <p class="post-meta">{{ entry.date?.slice(0, 10) }} <span v-if="entry.categories?.length">· {{ entry.categories.join(' / ') }}</span><span v-if="entry.tags?.length"> · {{ entry.tags.join(' · ') }}</span></p>
      <h1>{{ entry.title }}</h1>
      <p class="post-description" :class="{ 'project-detail__summary': kind === 'project' }">{{ entry.summary }}</p>
    </header>

    <figure v-if="entry.cover" class="post-cover" :class="{ 'project-detail__cover': kind === 'project' }">
      <img :src="entry.cover" :alt="entry.title">
    </figure>

    <div class="post-layout" :class="{ 'project-detail__content': kind === 'project' }">
      <aside v-if="kind === 'post' && headings.length > 2" class="toc" aria-label="文章目录">
        <details open>
          <summary>文章目录</summary>
          <nav><a v-for="heading in headings" :key="heading.id" :href="'#' + encodeURIComponent(heading.id)" :class="'toc-level-' + heading.level">{{ heading.text }}</a></nav>
        </details>
      </aside>
      <div class="post-content markdown-body" v-html="rendered"></div>
    </div>

    <section v-if="kind === 'post'" class="post-interactions">
      <div class="interaction-actions">
        <button :class="{ active: liked }" @click="action('likes')">♡ 点赞</button>
        <button :class="{ active: saved }" @click="action('bookmarks')">☆ 收藏</button>
        <span role="status">{{ notice }}</span>
      </div>
      <h2>评论 {{ comments.length }}</h2>
      <div v-for="item in comments" :key="item.id" class="comment-item">
        <div><strong>{{ item.nickname }}</strong><time>{{ new Date(item.created_at).toLocaleString('zh-CN') }}</time></div>
        <p>{{ item.content }}</p>
      </div>
      <form class="comment-form" @submit.prevent="submit">
        <textarea v-model="comment" rows="4" placeholder="写下友善、具体的评论……"></textarea>
        <button type="submit">发布评论</button>
      </form>
    </section>

    <footer v-if="kind === 'project'" class="project-detail__footer">
      <RouterLink to="/projects/">← 返回项目列表</RouterLink>
      <a href="https://github.com/banxia-prgo/picture_browser" target="_blank" rel="noopener">GitHub 源码 ↗</a>
    </footer>
  </article>
  <div v-else class="article-loading">正在加载内容，或暂未找到这篇文章。</div>
</template>

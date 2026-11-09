<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
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
  const tokens = markdown.parse(entry.value.content || '', {})
  const result: Array<{ level: number; text: string; id: string }> = []
  for (let index = 0; index < tokens.length; index += 1) {
    const token = tokens[index]
    if (!token || token.type !== 'heading_open') continue
    const inline = tokens[index + 1]
    const text = inline?.type === 'inline' ? inline.content : ''
    result.push({
      level: Number(token.tag.slice(1)),
      text,
      id: slugify(text) || `section-${result.length + 1}`,
    })
  }
  return result
})
let tocObserver: IntersectionObserver | null = null
let tocCleanup: (() => void) | null = null

const rendered = computed(() => {
  if (!entry.value) return ''
  let headingIndex = 0
  const renderer = new MarkdownIt({ html: false, linkify: true, typographer: true })
  renderer.renderer.rules.heading_open = (tokens, idx, options, _env, self) => {
    const heading = headings.value[headingIndex++]
    const token = tokens[idx]
    if (heading && token) token.attrSet('id', heading.id)
    return self.renderToken(tokens, idx, options)
  }
  return renderer.render(entry.value.content || '')
})

onMounted(async () => {
  const data = await loadCatalog()
  const list = kind === 'project' ? data.projects : data.posts
  entry.value = list.find(item => item.slug === String(route.params.slug)) || null
  await nextTick()
  initTableOfContents()
  if (kind === 'post') {
    try {
      const response = await api.get('/api/articles/' + String(route.params.slug) + '/comments')
      comments.value = response.data
    } catch {
      // The comments endpoint may not be available in the local API yet.
    }
  }
})


function initTableOfContents() {
  const toc = document.querySelector<HTMLElement>('.post-single .toc')
  const content = document.querySelector<HTMLElement>('.post-single .post-content')
  if (!toc || !content) return

  const links = Array.from(toc.querySelectorAll<HTMLAnchorElement>('a[href^="#"]'))
  const targets = links.map(link => {
    const id = decodeURIComponent(link.getAttribute('href')!.slice(1))
    return document.getElementById(id)
  }).filter((item): item is HTMLElement => Boolean(item))
  if (!targets.length) return

  const tocNav = toc.querySelector<HTMLElement>('nav')
  if (!tocNav) return

  const setActive = (heading: HTMLElement) => {
    links.forEach(link => {
      const id = decodeURIComponent(link.getAttribute('href')!.slice(1))
      const active = id === heading.id
      link.classList.toggle('toc-active', active)
      if (!active) return

      // Scroll the TOC list itself, keeping the active item visible without
      // moving the article page or the sticky sidebar.
      const navBox = tocNav.getBoundingClientRect()
      const linkBox = link.getBoundingClientRect()
      if (linkBox.top < navBox.top || linkBox.bottom > navBox.bottom) {
        const targetTop = tocNav.scrollTop + linkBox.top - navBox.top
          - (tocNav.clientHeight - linkBox.height) / 2
        tocNav.scrollTo({ top: Math.max(0, targetTop), behavior: 'smooth' })
      }
    })
  }

  tocObserver = new IntersectionObserver(entries => {
    const visible = entries
      .filter(item => item.isIntersecting)
      .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)
    const firstVisible = visible[0]
    if (firstVisible) {
      setActive(firstVisible.target as HTMLElement)
    } else {
      const passed = targets.filter(item => item.getBoundingClientRect().top <= 140)
      const activeTarget = passed[passed.length - 1] ?? targets[0]
      if (activeTarget) setActive(activeTarget)
    }
  }, { rootMargin: '-110px 0px -65% 0px', threshold: [0, 1] })

  targets.forEach(target => tocObserver?.observe(target))
  const firstTarget = targets[0]
  if (firstTarget) setActive(firstTarget)

  const desktop = window.matchMedia('(min-width: 1451px)')
  let handle: HTMLSpanElement | null = null
  let dragging = false
  const root = document.documentElement
  const onMove = (event: PointerEvent) => {
    if (!dragging) return
    const width = Math.max(180, Math.min(380, event.clientX - toc.getBoundingClientRect().left))
    root.style.setProperty('--toc-sidebar-width', width + 'px')
    root.style.setProperty('--toc-sidebar-gap', '40px')
    handle?.setAttribute('aria-valuenow', String(Math.round(width)))
  }
  const stopDragging = () => {
    dragging = false
    handle?.classList.remove('is-dragging')
    document.body.classList.remove('toc-is-resizing')
    document.removeEventListener('pointermove', onMove)
    document.removeEventListener('pointerup', stopDragging)
  }
  const addHandle = () => {
    if (!desktop.matches || handle) return
    handle = document.createElement('span')
    handle.className = 'toc-resize-handle'
    handle.setAttribute('role', 'separator')
    handle.setAttribute('aria-label', '调整目录宽度')
    handle.setAttribute('aria-orientation', 'vertical')
    handle.tabIndex = 0
    handle.addEventListener('pointerdown', event => {
      if (!desktop.matches) return
      dragging = true
      handle?.classList.add('is-dragging')
      document.body.classList.add('toc-is-resizing')
      document.addEventListener('pointermove', onMove)
      document.addEventListener('pointerup', stopDragging)
      event.preventDefault()
    })
    handle.addEventListener('keydown', event => {
      if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return
      const current = parseFloat(getComputedStyle(root).getPropertyValue('--toc-sidebar-width')) || 220
      const width = Math.max(180, Math.min(380, current + (event.key === 'ArrowRight' ? 10 : -10)))
      root.style.setProperty('--toc-sidebar-width', width + 'px')
      event.preventDefault()
    })
    toc.appendChild(handle)
  }
  addHandle()
  const onMediaChange = () => addHandle()
  desktop.addEventListener?.('change', onMediaChange)

  links.forEach(link => link.addEventListener('click', () => {
    const id = decodeURIComponent(link.getAttribute('href')!.slice(1))
    const heading = document.getElementById(id)
    if (heading) setActive(heading)
  }))

  tocCleanup = () => {
    tocObserver?.disconnect()
    tocObserver = null
    stopDragging()
    desktop.removeEventListener?.('change', onMediaChange)
    handle?.remove()
  }
}

onBeforeUnmount(() => tocCleanup?.())

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
  <article v-if="entry" :class="['post-single', { 'post-has-toc': kind === 'post' && headings.length > 2 }, kind === 'project' ? 'project-detail' : '']">
    <nav class="post-breadcrumb" aria-label="面包屑">
      <RouterLink to="/">首页</RouterLink><span>/</span>
      <RouterLink :to="kind === 'project' ? '/projects/' : '/posts/'">{{ kind === 'project' ? '项目' : '文章' }}</RouterLink><span>/</span>
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
      <a v-if="entry.github" :href="entry.github" target="_blank" rel="noopener noreferrer">GitHub 源码 ↗</a>
    </footer>
  </article>
  <div v-else class="article-loading">正在加载内容，或暂未找到这篇文章。</div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { loadCatalog, type ArticleContent } from '@/api/content'

const query = ref('')
const activeTag = ref('全部')
const sortMode = ref('newest')
const posts = ref<ArticleContent[]>([])

onMounted(async () => {
  try {
    posts.value = (await loadCatalog()).posts
  } catch (error) {
    console.error('加载随笔归档失败', error)
  }
})

const tags = computed(() => ['全部', ...new Set(posts.value.flatMap(post => post.tags || []))])
const filtered = computed(() => {
  const q = query.value.trim().toLocaleLowerCase()
  return posts.value
    .filter(post => activeTag.value === '全部' || (post.tags || []).includes(activeTag.value))
    .filter(post => !q || [post.title, post.summary, ...(post.tags || [])].join(' ').toLocaleLowerCase().includes(q))
    .slice()
    .sort((a, b) => {
      if (sortMode.value === 'oldest') return String(a.date || '').localeCompare(String(b.date || ''))
      if (sortMode.value === 'title') return a.title.localeCompare(b.title, 'zh-CN')
      return String(b.date || '').localeCompare(String(a.date || ''))
    })
})
</script>

<template>
  <div class="archive-page">
    <header class="archive-header">
      <p class="banxia-kicker">NOTES / THOUGHTS / LEARNING</p>
      <h1>技术随笔</h1>
      <p class="archive-description">记录编程学习、问题排查与项目实践中的思考。<br>让每一次学习，都成为下一次动手的起点。</p>
    </header>

    <section class="archive-toolbar" aria-label="随笔筛选">
      <label class="archive-search">
        <span aria-hidden="true">⌕</span>
        <input v-model="query" type="search" placeholder="搜索标题、摘要或标签">
      </label>
      <label class="archive-sort">
        <span>排序</span>
        <select v-model="sortMode">
          <option value="newest">最新发布</option>
          <option value="oldest">最早发布</option>
          <option value="title">标题</option>
        </select>
      </label>
    </section>

    <div class="archive-tags" aria-label="按标签筛选">
      <button
        v-for="tag in tags"
        :key="tag"
        type="button"
        :class="{ active: activeTag === tag }"
        :aria-pressed="activeTag === tag"
        @click="activeTag = tag"
      >{{ tag }}</button>
    </div>

    <div class="archive-results">
      <span>随笔归档</span>
      <span>显示 {{ filtered.length }} / {{ posts.length }} 篇</span>
    </div>

    <section class="post-list" aria-label="文章列表">
      <article v-for="post in filtered" :key="post.slug" class="post-entry">
        <header class="entry-header">
          <p class="entry-meta">{{ post.date?.slice(0, 10) }} <span v-if="post.categories?.length">· {{ post.categories.join(' / ') }}</span></p>
          <h2><RouterLink :to="post.href">{{ post.title }}</RouterLink></h2>
        </header>
        <div class="entry-content">{{ post.summary }}</div>
        <footer class="entry-footer">
          <div class="post-tags"><span v-for="tag in post.tags || []" :key="tag">{{ tag }}</span></div>
          <RouterLink :to="post.href" class="read-more">阅读全文 <span aria-hidden="true">↗</span></RouterLink>
        </footer>
      </article>
      <div v-if="!filtered.length" class="archive-empty">没有找到匹配的随笔，试试其他关键词或标签。</div>
    </section>
  </div>
</template>

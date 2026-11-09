import { ref } from 'vue'
import { api } from '@/api/client'
import type { Entry } from '@/data/site'

export interface ArticleContent extends Entry {
  content: string
  categories?: string[]
  cover?: string
  permalink: string
  weight?: number
  featured?: boolean
  tech?: string[]
  github?: string
}

interface Catalog {
  posts: ArticleContent[]
  projects: ArticleContent[]
}

interface ApiContent {
  kind: 'post' | 'project'
  slug: string
  title: string
  summary: string
  content: string
  featured?: boolean
  cover_url?: string | null
  github_url?: string | null
  categories?: Array<{ name: string }>
  tags?: Array<{ name: string }>
  published_at?: string | null
  created_at?: string | null
  sort_order?: number
}

const catalog = ref<Catalog>({ posts: [], projects: [] })
const loaded = ref(false)
let loadedAt = 0
const CACHE_TTL_MS = 15_000

function mapContent(item: ApiContent): ArticleContent {
  const href = item.kind === 'project'
    ? `/projects/${encodeURIComponent(item.slug)}/`
    : `/posts/${encodeURIComponent(item.slug)}/`
  const tags = (item.tags || []).map(tag => tag.name).filter(Boolean)
  return {
    slug: item.slug,
    title: item.title,
    summary: item.summary || '',
    date: item.published_at || item.created_at || '',
    tags,
    category: item.kind,
    href,
    content: item.content || '',
    categories: (item.categories || []).map(category => category.name).filter(Boolean),
    cover: item.cover_url || undefined,
    permalink: href,
    featured: Boolean(item.featured),
    weight: item.sort_order,
    tech: tags,
    github: item.github_url || undefined,
  }
}

export function invalidateCatalog(): void {
  loaded.value = false
  loadedAt = 0
}

export async function loadCatalog(forceRefresh = false): Promise<Catalog> {
  if (!forceRefresh && loaded.value && Date.now() - loadedAt < CACHE_TTL_MS) {
    return catalog.value
  }

  try {
    const [postsResponse, projectsResponse] = await Promise.all([
      api.get<ApiContent[]>('/api/content/posts?limit=100'),
      api.get<ApiContent[]>('/api/content/projects?limit=100'),
    ])
    catalog.value = {
      posts: postsResponse.data.map(mapContent),
      projects: projectsResponse.data.map(mapContent),
    }
    loaded.value = true
    loadedAt = Date.now()
    return catalog.value
  } catch (apiError) {
    // Keep the last generated public catalogue available during a temporary API outage.
    try {
      const response = await fetch('/content/catalog.json', { cache: 'no-cache' })
      if (!response.ok) throw new Error('静态内容目录不可用')
      catalog.value = await response.json() as Catalog
      loaded.value = true
      loadedAt = Date.now()
      return catalog.value
    } catch {
      if (!import.meta.env.DEV) throw apiError
      // Local preview fallback only; production content is managed by the CMS API.
      const { entries } = await import('@/data/site')
      catalog.value = {
        posts: entries.filter(entry => entry.category === 'post').map(entry => ({
          ...entry, content: '', permalink: entry.href,
        })),
        projects: entries.filter(entry => entry.category === 'project').map(entry => ({
          ...entry, content: '', permalink: entry.href,
        })),
      }
      loaded.value = true
      loadedAt = Date.now()
      return catalog.value
    }
  }
}

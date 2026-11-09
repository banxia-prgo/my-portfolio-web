import { ref } from 'vue'
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

const catalog = ref<Catalog>({ posts: [], projects: [] })
const loaded = ref(false)

export async function loadCatalog(): Promise<Catalog> {
  if (loaded.value) return catalog.value

  try {
    const response = await fetch('/content/catalog.json', { cache: 'no-cache' })
    if (!response.ok) throw new Error('Content catalogue not generated')
    catalog.value = await response.json() as Catalog
  } catch {
    // Preview fallback only. Run scripts/migrate_hugo_content.py to import original Hugo Page Bundles.
    const { entries } = await import('@/data/site')
    catalog.value = {
      posts: entries.filter(entry => entry.category === 'post').map(entry => ({
        ...entry, content: '', permalink: entry.href,
      })),
      projects: entries.filter(entry => entry.category === 'project').map(entry => ({
        ...entry, content: '', permalink: entry.href,
      })),
    }
  }

  loaded.value = true
  return catalog.value
}

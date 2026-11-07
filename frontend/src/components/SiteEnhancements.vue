<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
let progress: HTMLDivElement | null = null
let backTop: HTMLButtonElement | null = null
let lightbox: HTMLDivElement | null = null
let preview: HTMLImageElement | null = null
let closeButton: HTMLButtonElement | null = null
let previousFocus: HTMLElement | null = null
let revealObserver: IntersectionObserver | null = null
let imageCleanups: Array<() => void> = []
let scrollScheduled = false
const reduceMotion = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches

function updateScrollUI() {
  const scrollable = document.documentElement.scrollHeight - window.innerHeight
  const percent = scrollable > 0 ? Math.min(100, Math.max(0, window.scrollY / scrollable * 100)) : 0
  if (progress) progress.style.width = percent + '%'
  backTop?.classList.toggle('is-visible', window.scrollY > 480)
  scrollScheduled = false
}
function onScroll() {
  if (scrollScheduled) return
  scrollScheduled = true
  window.requestAnimationFrame(updateScrollUI)
}
function closeLightbox() {
  if (!lightbox?.classList.contains('is-open')) return
  lightbox.classList.remove('is-open')
  document.body.classList.remove('bx-lightbox-open')
  preview?.removeAttribute('src')
  previousFocus?.focus()
}
function openLightbox(image: HTMLImageElement) {
  if (!lightbox || !preview || !closeButton) return
  previousFocus = image
  preview.src = image.currentSrc || image.src
  preview.alt = image.alt || '文章图片'
  lightbox.classList.add('is-open')
  document.body.classList.add('bx-lightbox-open')
  closeButton.focus()
}
function onKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') closeLightbox()
  if (event.key === 'Tab' && lightbox?.classList.contains('is-open')) {
    event.preventDefault()
    closeButton?.focus()
  }
}
function clearArticleEnhancements() {
  imageCleanups.forEach(cleanup => cleanup())
  imageCleanups = []
  revealObserver?.disconnect()
  revealObserver = null
  lightbox?.remove()
  lightbox = null
  preview = null
  closeButton = null
}
async function attachArticleEnhancements() {
  await nextTick()
  clearArticleEnhancements()
  const article = document.querySelector<HTMLElement>('.post-single .post-content')
  const meta = document.querySelector<HTMLElement>('.post-single .post-meta')
  if (article && meta && !meta.querySelector('.bx-reading-time')) {
    const text = (article.innerText || article.textContent || '').replace(/\s+/g, '')
    const chineseChars = (text.match(/[\u3400-\u9fff]/g) || []).length
    const latinWords = (text.match(/[A-Za-z0-9_+#.-]+/g) || []).length
    const hint = document.createElement('span')
    hint.className = 'bx-reading-time'
    hint.textContent = '· 约 ' + Math.max(1, Math.ceil(chineseChars / 450 + latinWords / 180)) + ' 分钟阅读'
    meta.appendChild(hint)
  }

  if (article) {
    const images = Array.from(article.querySelectorAll('img')).filter(image => !image.closest('a'))
    if (images.length) {
      lightbox = document.createElement('div')
      lightbox.className = 'bx-lightbox'
      lightbox.setAttribute('role', 'dialog')
      lightbox.setAttribute('aria-modal', 'true')
      lightbox.setAttribute('aria-label', '图片预览')
      lightbox.innerHTML = '<button class="bx-lightbox__close" type="button" aria-label="关闭图片预览">×</button><img alt="">'
      document.body.appendChild(lightbox)
      preview = lightbox.querySelector('img')
      closeButton = lightbox.querySelector('button')
      images.forEach(image => {
        const oldTabIndex = image.getAttribute('tabindex')
        const oldRole = image.getAttribute('role')
        const oldLabel = image.getAttribute('aria-label')
        image.tabIndex = 0
        image.setAttribute('role', 'button')
        image.setAttribute('aria-label', (image.alt || '打开图片') + '（放大查看）')
        const click = () => openLightbox(image)
        const key = (event: KeyboardEvent) => {
          if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault()
            openLightbox(image)
          }
        }
        image.addEventListener('click', click)
        image.addEventListener('keydown', key)
        imageCleanups.push(() => {
          image.removeEventListener('click', click)
          image.removeEventListener('keydown', key)
          if (oldTabIndex === null) image.removeAttribute('tabindex'); else image.setAttribute('tabindex', oldTabIndex)
          if (oldRole === null) image.removeAttribute('role'); else image.setAttribute('role', oldRole)
          if (oldLabel === null) image.removeAttribute('aria-label'); else image.setAttribute('aria-label', oldLabel)
        })
      })
      closeButton?.addEventListener('click', closeLightbox)
      lightbox.addEventListener('click', event => { if (event.target === lightbox) closeLightbox() })
    }
  }

  if (!reduceMotion() && 'IntersectionObserver' in window) {
    const targets = document.querySelectorAll('.bx-project-card, .project-archive-card, .bx-learning-card, .bx-stats-card')
    revealObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return
        entry.target.classList.add('bx-in-view')
        revealObserver?.unobserve(entry.target)
      })
    }, { threshold: 0.08 })
    targets.forEach(element => {
      element.classList.add('bx-reveal-ready')
      revealObserver?.observe(element)
    })
  }
}

onMounted(() => {
  progress = document.createElement('div')
  progress.className = 'bx-site-progress'
  progress.setAttribute('aria-hidden', 'true')
  document.body.appendChild(progress)
  backTop = document.createElement('button')
  backTop.className = 'bx-back-top'
  backTop.type = 'button'
  backTop.setAttribute('aria-label', '返回页面顶部')
  backTop.title = '返回顶部'
  backTop.textContent = '↑'
  backTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: reduceMotion() ? 'auto' : 'smooth' }))
  document.body.appendChild(backTop)
  window.addEventListener('scroll', onScroll, { passive: true })
  window.addEventListener('resize', onScroll, { passive: true })
  document.addEventListener('keydown', onKeydown)
  updateScrollUI()
  attachArticleEnhancements()
})
watch(() => route.fullPath, () => attachArticleEnhancements())
onBeforeUnmount(() => {
  window.removeEventListener('scroll', onScroll)
  window.removeEventListener('resize', onScroll)
  document.removeEventListener('keydown', onKeydown)
  clearArticleEnhancements()
  progress?.remove()
  backTop?.remove()
})
</script>

<template><span class="site-enhancements-anchor" aria-hidden="true"></span></template>

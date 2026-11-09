<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useRoute } from 'vue-router'
import { api } from '@/api/client'

interface GuestbookMessage { id: number; content: string; nickname: string; created_at: string }
const route = useRoute()
const messages = ref<GuestbookMessage[]>([])
const content = ref('')
const isLoggedIn = ref(false)
const loading = ref(true)
const submitting = ref(false)
const notice = ref('')
const error = ref('')

async function loadMessages() {
  const response = await api.get('/api/guestbook/messages')
  messages.value = response.data
}

onMounted(async () => {
  try {
    await loadMessages()
    try {
      await api.get('/api/users/me')
      isLoggedIn.value = true
    } catch {
      isLoggedIn.value = false
    }
  } catch (e) {
    error.value = e instanceof Error ? e.message : '留言暂时无法加载，请稍后再试。'
  } finally {
    loading.value = false
  }
})

async function submitMessage() {
  if (!content.value.trim() || submitting.value) return
  submitting.value = true
  notice.value = ''
  error.value = ''
  try {
    await api.post('/api/guestbook/messages', { content: content.value.trim() })
    content.value = ''
    notice.value = '留言已发布，感谢你的分享。'
    await loadMessages()
  } catch (e) {
    error.value = e instanceof Error ? e.message : '留言提交失败，请稍后重试。'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="guestbook-page">
    <header class="guestbook-hero">
      <p class="banxia-kicker">GUESTBOOK / SAY HELLO</p>
      <h1>留言板</h1>
      <p>感谢你来到半夏小筑。无论是技术交流、文章反馈，还是简单地打声招呼，<br>都欢迎在这里留下你的想法。</p>
      <span class="guestbook-count">{{ messages.length }} 条公开留言</span>
    </header>

    <section class="guestbook-compose">
      <div class="guestbook-compose__heading"><span>✎</span><div><h2>写下你的留言</h2><p>期待与你交流，也请保持友善与尊重。</p></div></div>
      <template v-if="isLoggedIn">
        <form @submit.prevent="submitMessage">
          <textarea v-model="content" maxlength="2000" rows="5" placeholder="想说些什么？（最多 2000 字）" required></textarea>
          <div class="guestbook-compose__footer"><span>{{ content.length }} / 2000</span><button type="submit" :disabled="submitting || !content.trim()">{{ submitting ? '发布中…' : '发布留言 →' }}</button></div>
        </form>
      </template>
      <div v-else class="guestbook-login-prompt">
        <p>登录后即可发表留言，与半夏和其他访客交流。</p>
        <RouterLink :to="{ path: '/login/', query: { redirect: route.fullPath } }">登录后留言 →</RouterLink>
        <span>还没有账号？<RouterLink :to="{ path: '/register/', query: { redirect: route.fullPath } }">立即注册</RouterLink></span>
      </div>
      <p v-if="notice" class="guestbook-notice" role="status">{{ notice }}</p>
      <p v-if="error" class="guestbook-error" role="alert">{{ error }}</p>
    </section>

    <section class="guestbook-list">
      <div class="guestbook-list__heading"><h2>大家的留言</h2><span>SHARED THOUGHTS</span></div>
      <div v-if="loading" class="guestbook-empty">正在加载留言…</div>
      <div v-else-if="!messages.length" class="guestbook-empty"><span>☁</span><p>这里还很安静，期待你的第一条留言。</p></div>
      <article v-for="message in messages" :key="message.id" class="guestbook-message">
        <span class="guestbook-message__avatar">{{ message.nickname.slice(0, 1) || '友' }}</span>
        <div class="guestbook-message__body">
          <div class="guestbook-message__meta"><strong>{{ message.nickname }}</strong><time>{{ new Date(message.created_at).toLocaleString('zh-CN') }}</time></div>
          <p>{{ message.content }}</p>
        </div>
      </article>
    </section>
  </div>
</template>

<style scoped>
.guestbook-page{max-width:900px;margin:0 auto;padding:3.5rem 0 2rem}.guestbook-hero{padding:0 0 2rem;border-bottom:1px solid var(--border)}.guestbook-hero h1{margin:.5rem 0 .8rem;color:var(--primary);font-family:"STKaiti","KaiTi",serif;font-size:clamp(2.5rem,6vw,4rem);letter-spacing:.04em}.guestbook-hero>p:not(.banxia-kicker){color:var(--secondary);font-size:.9rem;line-height:1.9}.guestbook-count{display:inline-block;margin-top:.8rem;padding:.4rem .75rem;border-radius:999px;background:#f0edff;color:#7467bf;font-size:.7rem}.guestbook-compose{margin:2rem 0 3rem;padding:1.5rem;border:1px solid var(--border);border-radius:18px;background:var(--entry)}.guestbook-compose__heading{display:flex;align-items:center;gap:12px;margin-bottom:1.2rem}.guestbook-compose__heading>span{display:grid;place-items:center;width:40px;height:40px;border-radius:13px;background:#f0edff;color:#7668c4;font-size:20px}.guestbook-compose h2,.guestbook-list h2{margin:0;color:var(--primary);font-size:1.1rem}.guestbook-compose__heading p{margin:4px 0 0;color:var(--secondary);font-size:.72rem}.guestbook-compose textarea{width:100%;padding:14px;border:1px solid var(--border);border-radius:12px;outline-color:#b9afe8;color:var(--primary);background:#fdfcff;resize:vertical;font:inherit;font-size:.85rem;line-height:1.8}.guestbook-compose__footer{display:flex;align-items:center;justify-content:space-between;margin-top:12px;color:var(--secondary);font-size:.68rem}.guestbook-compose__footer button,.guestbook-login-prompt>a{padding:10px 17px;border:0;border-radius:999px;background:#8170cc;color:#fff;font-size:.75rem;font-weight:700}.guestbook-compose__footer button:disabled{opacity:.5;cursor:not-allowed}.guestbook-login-prompt{display:flex;align-items:center;flex-wrap:wrap;gap:12px}.guestbook-login-prompt p{flex-basis:100%;margin:0;color:var(--secondary);font-size:.82rem}.guestbook-login-prompt span{color:var(--secondary);font-size:.72rem}.guestbook-login-prompt span a{color:#7668c4}.guestbook-notice,.guestbook-error{margin:.8rem 0 0;font-size:.75rem}.guestbook-notice{color:#398b78}.guestbook-error{color:#c45465}.guestbook-list__heading{display:flex;align-items:center;justify-content:space-between;margin-bottom:1rem}.guestbook-list__heading span{color:#9a91c5;font-size:.62rem;letter-spacing:.15em}.guestbook-empty{padding:2.5rem 1rem;border:1px dashed var(--border);border-radius:14px;color:var(--secondary);text-align:center;font-size:.8rem}.guestbook-empty>span{font-size:1.7rem}.guestbook-message{display:flex;gap:14px;padding:1.25rem 0;border-bottom:1px solid var(--border)}.guestbook-message__avatar{flex:0 0 40px;width:40px;height:40px;display:grid;place-items:center;border-radius:14px;background:linear-gradient(145deg,#e9e4ff,#e1f5f2);color:#7163bd;font-size:1.1rem}.guestbook-message__body{min-width:0;flex:1}.guestbook-message__meta{display:flex;align-items:center;flex-wrap:wrap;gap:12px}.guestbook-message__meta strong{color:var(--primary);font-size:.8rem}.guestbook-message__meta time{color:var(--secondary);font-size:.65rem}.guestbook-message__body p{margin:.55rem 0 0;color:var(--primary);font-size:.85rem;line-height:1.85;white-space:pre-wrap;overflow-wrap:anywhere}@media(max-width:720px){.guestbook-page{width:calc(100% - 32px);padding-top:2.5rem}.guestbook-compose{padding:1.1rem}.guestbook-hero br{display:none}}
</style>

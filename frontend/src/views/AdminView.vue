<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { api } from '@/api/client'

type Tab = 'overview' | 'content' | 'users' | 'audit' | 'settings'
type ContentKind = 'post' | 'project'
interface ContentRow {
  id: number
  kind: ContentKind
  slug: string
  title: string
  summary: string
  content: string
  status: 'draft' | 'published' | 'archived'
  featured: boolean
  sort_order: number
  cover_url: string | null
  github_url: string | null
}
interface UserRow {
  id: number
  email: string
  nickname: string
  role: string
  is_active: boolean
  created_at: string
}
interface Overview {
  users: number
  active_users: number
  comments: number
  guestbook_messages: number
}

const tab = ref<Tab>('overview')
const loading = ref(false)
const message = ref('')
const overview = ref<Overview>({ users: 0, active_users: 0, comments: 0, guestbook_messages: 0 })
const users = ref<UserRow[]>([])
const contentItems = ref<ContentRow[]>([])
const auditLogs = ref<Record<string, unknown>[]>([])
const editingId = ref<number | null>(null)
const editorOpen = ref(false)
const draft = reactive({
  kind: 'post' as ContentKind,
  slug: '',
  title: '',
  summary: '',
  content: '',
  status: 'draft' as ContentRow['status'],
  featured: false,
  sort_order: 0,
  cover_url: '',
  github_url: '',
})
const siteProfile = ref('')

function resetDraft() {
  editingId.value = null
  Object.assign(draft, {
    kind: 'post', slug: '', title: '', summary: '', content: '',
    status: 'draft', featured: false, sort_order: 0, cover_url: '', github_url: '',
  })
}

async function loadOverview() {
  const response = await api.get<Overview>('/api/admin/overview')
  overview.value = response.data
}
async function loadUsers() {
  const response = await api.get<{ items: UserRow[] }>('/api/admin/users')
  users.value = response.data.items
}
async function loadContent() {
  const response = await api.get<ContentRow[]>('/api/admin/content')
  contentItems.value = response.data
}
async function loadAudit() {
  const response = await api.get<Record<string, unknown>[]>('/api/admin/audit-logs')
  auditLogs.value = response.data
}
async function loadSettings() {
  const response = await api.get<Record<string, unknown>>('/api/site/profile')
  siteProfile.value = JSON.stringify(response.data, null, 2)
}
async function refreshAll() {
  loading.value = true
  message.value = ''
  try {
    await Promise.all([loadOverview(), loadUsers(), loadContent(), loadAudit()])
  } catch (error) {
    message.value = error instanceof Error ? error.message : '加载后台数据失败'
  } finally {
    loading.value = false
  }
}
function editContent(item: ContentRow) {
  editingId.value = item.id
  Object.assign(draft, {
    kind: item.kind, slug: item.slug, title: item.title, summary: item.summary,
    content: item.content, status: item.status, featured: item.featured,
    sort_order: item.sort_order, cover_url: item.cover_url || '', github_url: item.github_url || '',
  })
  editorOpen.value = true
}
async function saveContent() {
  message.value = ''
  const payload = { ...draft, cover_url: draft.cover_url || null, github_url: draft.github_url || null }
  try {
    if (editingId.value) await api.patch(`/api/admin/content/${editingId.value}`, payload)
    else await api.post('/api/admin/content', payload)
    editorOpen.value = false
    resetDraft()
    await loadContent()
    message.value = '内容已保存'
  } catch (error) {
    message.value = error instanceof Error ? error.message : '保存失败'
  }
}
async function deleteContent(item: ContentRow) {
  if (!window.confirm(`确定删除「${item.title}」吗？`)) return
  try {
    await api.delete(`/api/admin/content/${item.id}`)
    await loadContent()
    message.value = '内容已删除'
  } catch (error) {
    message.value = error instanceof Error ? error.message : '删除失败'
  }
}
async function toggleUser(user: UserRow) {
  try {
    await api.patch(`/api/admin/users/${user.id}`, { is_active: !user.is_active })
    await loadUsers()
    message.value = '用户状态已更新'
  } catch (error) {
    message.value = error instanceof Error ? error.message : '更新失败'
  }
}
async function saveProfile() {
  try {
    const value = JSON.parse(siteProfile.value) as Record<string, unknown>
    await api.put('/api/admin/site-settings/profile', { value })
    message.value = '关于我资料已保存'
  } catch (error) {
    message.value = error instanceof Error ? error.message : 'JSON 格式不正确或保存失败'
  }
}

onMounted(() => { void refreshAll() })
</script>

<template>
  <section class="admin-page">
    <header class="admin-heading">
      <div>
        <p class="admin-kicker">BANXIA STUDIO / CONTROL ROOM</p>
        <h1>管理后台</h1>
        <p>内容、用户与网站运行情况，一处管理。</p>
      </div>
      <button class="admin-refresh" :disabled="loading" @click="refreshAll">{{ loading ? '加载中…' : '刷新数据' }}</button>
    </header>

    <nav class="admin-tabs" aria-label="后台功能">
      <button v-for="item in [
        { id: 'overview', label: '总览' }, { id: 'content', label: '内容管理' },
        { id: 'users', label: '用户管理' }, { id: 'audit', label: '操作日志' },
        { id: 'settings', label: '关于我' },
      ]" :key="item.id" :class="{ active: tab === item.id }" @click="tab = item.id as Tab; if (item.id === 'settings') loadSettings()">
        {{ item.label }}
      </button>
    </nav>

    <p v-if="message" class="admin-message" role="status">{{ message }}</p>

    <section v-if="tab === 'overview'" class="admin-stats">
      <article><span>注册用户</span><strong>{{ overview.users }}</strong></article>
      <article><span>正常用户</span><strong>{{ overview.active_users }}</strong></article>
      <article><span>文章评论</span><strong>{{ overview.comments }}</strong></article>
      <article><span>公开留言</span><strong>{{ overview.guestbook_messages }}</strong></article>
      <article><span>内容条目</span><strong>{{ contentItems.length }}</strong></article>
    </section>

    <section v-else-if="tab === 'content'" class="admin-panel">
      <div class="admin-panel-heading">
        <div><h2>文章与项目</h2><p>支持草稿、发布和归档。</p></div>
        <button class="admin-primary" @click="resetDraft(); editorOpen = !editorOpen">新建内容</button>
      </div>
      <form v-if="editorOpen" class="admin-editor" @submit.prevent="saveContent">
        <div class="admin-form-grid">
          <label>内容类型<select v-model="draft.kind"><option value="post">文章</option><option value="project">项目</option></select></label>
          <label>状态<select v-model="draft.status"><option value="draft">草稿</option><option value="published">已发布</option><option value="archived">归档</option></select></label>
          <label>标题<input v-model="draft.title" required maxlength="240"></label>
          <label>Slug<input v-model="draft.slug" required maxlength="180"></label>
          <label class="wide">摘要<input v-model="draft.summary" maxlength="600"></label>
          <label>封面 URL<input v-model="draft.cover_url"></label>
          <label>GitHub URL<input v-model="draft.github_url"></label>
          <label class="wide">Markdown 正文<textarea v-model="draft.content" rows="12" maxlength="200000"></textarea></label>
          <label class="admin-check"><input v-model="draft.featured" type="checkbox"> 首页精选</label>
        </div>
        <div class="admin-form-actions"><button class="admin-primary" type="submit">保存内容</button><button type="button" class="admin-secondary" @click="editorOpen = false; resetDraft()">取消</button></div>
      </form>
      <div class="admin-table-wrap">
        <table><thead><tr><th>标题</th><th>类型</th><th>状态</th><th>更新时间</th><th>操作</th></tr></thead>
          <tbody><tr v-for="item in contentItems" :key="item.id">
            <td><strong>{{ item.title }}</strong><small>{{ item.slug }}</small></td>
            <td>{{ item.kind === 'post' ? '文章' : '项目' }}</td><td>{{ item.status }}</td>
            <td>{{ item.id }}</td>
            <td><button class="admin-link" @click="editContent(item)">编辑</button><button class="admin-link danger" @click="deleteContent(item)">删除</button></td>
          </tr><tr v-if="!contentItems.length"><td colspan="5" class="empty">还没有数据库内容。现有 Hugo 内容目录暂时保留，不会自动删除。</td></tr></tbody>
        </table>
      </div>
    </section>

    <section v-else-if="tab === 'users'" class="admin-panel">
      <div class="admin-panel-heading"><div><h2>用户管理</h2><p>查看注册用户并管理账号状态。</p></div></div>
      <div class="admin-table-wrap"><table><thead><tr><th>用户</th><th>邮箱</th><th>角色</th><th>状态</th><th>操作</th></tr></thead>
        <tbody><tr v-for="user in users" :key="user.id"><td>{{ user.nickname }}</td><td>{{ user.email }}</td><td>{{ user.role }}</td><td>{{ user.is_active ? '正常' : '已停用' }}</td><td><button class="admin-link" @click="toggleUser(user)">{{ user.is_active ? '停用' : '启用' }}</button></td></tr></tbody>
      </table></div>
    </section>

    <section v-else-if="tab === 'audit'" class="admin-panel">
      <div class="admin-panel-heading"><div><h2>管理员操作日志</h2><p>记录后台关键操作。</p></div></div>
      <div class="admin-table-wrap"><table><thead><tr><th>操作</th><th>对象</th><th>详情</th><th>时间</th></tr></thead>
        <tbody><tr v-for="(log, index) in auditLogs" :key="String(log.id || index)"><td>{{ log.action }}</td><td>{{ log.target_type }} / {{ log.target_id }}</td><td>{{ log.detail }}</td><td>{{ log.created_at }}</td></tr></tbody>
      </table></div>
    </section>

    <section v-else class="admin-panel">
      <div class="admin-panel-heading"><div><h2>关于我资料</h2><p>以 JSON 格式编辑公开资料。</p></div></div>
      <textarea v-model="siteProfile" class="admin-json-editor" rows="18" spellcheck="false"></textarea>
      <button class="admin-primary" @click="saveProfile">保存资料</button>
    </section>
  </section>
</template>

<style scoped>
.admin-page{width:min(1180px,calc(100% - 48px));margin:64px auto 100px;color:#29263a}
.admin-heading,.admin-panel-heading{display:flex;align-items:center;justify-content:space-between;gap:20px}
.admin-kicker{font:11px 'DM Mono',monospace;letter-spacing:.16em;color:#7564c1}
.admin-heading h1{margin:10px 0;font-size:clamp(34px,5vw,52px);letter-spacing:-.05em}
.admin-heading p,.admin-panel-heading p{color:#817d91;font-size:13px}
.admin-refresh,.admin-secondary{background:white;border:1px solid #e5e0f2;border-radius:999px;padding:11px 18px;color:#6655ad}
.admin-tabs{display:flex;gap:8px;flex-wrap:wrap;margin:34px 0 22px;border-bottom:1px solid #eae7f2}
.admin-tabs button{border:0;background:transparent;padding:13px 17px;color:#817d91}
.admin-tabs button.active{color:#6e5cbd;border-bottom:2px solid #8b79d6}
.admin-message{padding:12px 16px;background:#f0edff;border-radius:12px;color:#6252a8}
.admin-stats{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:14px}
.admin-stats article,.admin-panel{background:#fff;border:1px solid #eae7f2;border-radius:18px;padding:22px}
.admin-stats article span{display:block;color:#817d91;font-size:12px}
.admin-stats article strong{display:block;margin-top:14px;font-size:32px}
.admin-panel-heading h2{margin:0;font-size:21px}
.admin-primary{border:0;border-radius:999px;background:#7564c1;color:white;padding:11px 20px}
.admin-editor{margin:22px 0;padding:20px;background:#fbfaff;border:1px solid #eae7f2;border-radius:14px}
.admin-form-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.admin-form-grid label{display:grid;gap:7px;font-size:12px;color:#6f6a80}
.admin-form-grid input,.admin-form-grid select,.admin-form-grid textarea,.admin-json-editor{width:100%;border:1px solid #e5e0f2;border-radius:10px;padding:11px;background:white;color:#29263a;font:inherit}
.admin-form-grid .wide{grid-column:1/-1}
.admin-form-grid .admin-check{display:flex;align-items:center}
.admin-form-actions{display:flex;gap:10px;margin-top:16px}
.admin-table-wrap{overflow-x:auto;margin-top:20px}
table{width:100%;border-collapse:collapse;text-align:left;font-size:13px}
th,td{padding:14px 12px;border-bottom:1px solid #eeeaf5;white-space:nowrap}
th{color:#817d91;font-weight:500}
td strong,td small{display:block}td small{margin-top:4px;color:#9993a8}
.admin-link{border:0;background:none;color:#6e5cbd;margin-right:12px}.admin-link.danger{color:#bd5b70}
.empty{text-align:center;color:#817d91;padding:30px}
.admin-json-editor{margin:20px 0;font:13px/1.7 'DM Mono',monospace}
@media(max-width:760px){.admin-page{width:calc(100% - 32px);margin-top:36px}.admin-stats{grid-template-columns:repeat(2,minmax(0,1fr))}.admin-form-grid{grid-template-columns:1fr}.admin-form-grid .wide{grid-column:auto}.admin-heading{align-items:flex-start;flex-direction:column}.admin-panel{padding:15px}}
</style>

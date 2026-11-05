<script setup lang="ts">
import {computed,onMounted,ref} from 'vue'
import {loadCatalog,type ArticleContent} from '@/api/content'
import EntryCard from '@/components/EntryCard.vue'
const q=ref(''),tag=ref('全部'),all=ref<ArticleContent[]>([])
onMounted(async()=>{all.value=(await loadCatalog()).posts})
const tags=computed(()=>['全部',...new Set(all.value.flatMap(e=>e.tags||[]))])
const filtered=computed(()=>all.value.filter(e=>tag.value==='全部'||e.tags?.includes(tag.value)).filter(e=>(e.title+e.summary+(e.tags||[]).join(' ')).toLowerCase().includes(q.value.toLowerCase())))
</script>
<template><div class="page-wrap archive"><header><span class="eyebrow">THE JOURNAL / FIELD NOTES</span><h1 class="page-title">技术随笔<span>。</span></h1><p class="page-lead">记录编程学习、问题排查与项目实践中的思考。<br>让每一次学习，都成为下一次动手的起点。</p></header><div class="tools"><input v-model="q" placeholder="搜索标题、摘要或标签..."/><button v-for="t in tags" :key="t" :class="{active:tag===t}" @click="tag=t">{{t}}</button></div><p class="count">SHOWING {{filtered.length}} NOTES</p><div class="grid"><EntryCard v-for="(e,i) in filtered" :key="e.slug" :entry="e" :index="i"/></div><p v-if="!filtered.length" class="empty">没有找到匹配的随笔。</p></div></template>
<style scoped>.archive{padding-top:75px}header{padding-bottom:45px;border-bottom:1px solid #eae7f2}.page-title span{color:#8b79d6}.tools{display:flex;gap:9px;flex-wrap:wrap;padding:25px 0}.tools input{height:39px;min-width:240px;padding:0 12px;border:1px solid #e7e3f0;border-radius:10px;outline-color:#a99cdd}.tools button{padding:8px 12px;border:1px solid #e8e4f1;border-radius:99px;background:white;color:#777286;font-size:10px}.tools button.active{background:#eeeaff;border-color:#d9d1f4;color:#6e5cbd}.count{color:#a09aad;font:9px 'DM Mono';letter-spacing:.14em}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}.empty{text-align:center;padding:50px;color:#817d91}@media(max-width:650px){.archive{padding-top:45px}.grid{grid-template-columns:1fr}}</style>
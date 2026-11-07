<script setup lang="ts">
import type { Entry } from '@/data/site'
defineProps<{entry:Entry;index?:number}>()
</script>
<template><RouterLink :to="entry.href" class="entry-card"><div class="meta"><span>{{String((index??0)+1).padStart(2,'0')}}</span><span>{{entry.category==='project'?'PROJECT':'JOURNAL'}}</span></div><h3>{{entry.title}}</h3><p>{{entry.summary}}</p><div class="bottom"><time>{{entry.date}}</time><div><span v-for="tag in entry.tags.slice(0,3)" :key="tag">{{tag}}</span></div></div></RouterLink></template>
<style scoped>
.entry-card{display:flex;flex-direction:column;min-height:240px;padding:24px;border:1px solid #eae7f2;border-radius:18px;background:#ffffffc9;transition:.25s}.entry-card:hover{transform:translateY(-5px);border-color:#c9c0ed;box-shadow:0 18px 40px #7868b51a}.meta,.bottom{display:flex;justify-content:space-between;color:#918ba2;font:10px 'DM Mono',monospace}.entry-card h3{margin:35px 0 10px;font-size:21px;letter-spacing:-.04em}.entry-card p{margin:0;color:#817d91;font-size:13px;line-height:1.8}.bottom{margin-top:auto;padding-top:25px;align-items:center;font-family:inherit}.bottom div{display:flex;gap:6px}.bottom div span{padding:4px 8px;border-radius:99px;background:#f1effb;color:#7668b4;font-size:10px}
</style>

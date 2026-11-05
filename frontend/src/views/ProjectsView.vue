<script setup lang="ts">
import {computed,ref} from 'vue'
import {entries} from '@/data/site'
import EntryCard from '@/components/EntryCard.vue'
const q=ref('')
const projects=computed(()=>entries.filter(e=>e.category==='project').filter(e=>(e.title+e.summary+e.tags.join(' ')).toLowerCase().includes(q.value.toLowerCase())))
</script>
<template><div class="page-wrap projects"><header><span class="eyebrow">SELECTED WORK / EXPERIMENTS</span><h1 class="page-title">项目作品<span>。</span></h1><p class="page-lead">把学习与想法做成可以运行、可以复现的项目。<br>记录目标、设计、实现与复盘。</p></header><input v-model="q" class="search" placeholder="搜索项目或技术栈"><div class="grid"><EntryCard v-for="(e,i) in projects" :key="e.slug" :entry="e" :index="i"/></div></div></template>
<style scoped>.projects{padding-top:75px}header{padding-bottom:40px;border-bottom:1px solid #eae7f2}.page-title span{color:#8b79d6}.search{margin:25px 0;padding:12px 14px;width:min(360px,100%);border:1px solid #e7e3f0;border-radius:10px;outline-color:#a99cdd}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}@media(max-width:650px){.projects{padding-top:45px}.grid{grid-template-columns:1fr}}</style>

<script setup lang="ts">
import {onMounted,ref} from 'vue'
import {api} from '@/api/client'
interface Profile{email:string;nickname:string;avatar_url?:string|null}
const profile=ref<Profile|null>(null),error=ref('')
onMounted(async()=>{try{const r=await api.get('/api/users/me');profile.value=r.data}catch{error.value='暂时无法读取个人资料，请确认已登录且后端认证接口已部署。'}})
</script>
<template><div class="page-wrap profile"><span class="eyebrow">YOUR SPACE / ACCOUNT</span><h1 class="page-title">个人中心<span>。</span></h1><div v-if="profile" class="user-card"><div class="avatar">{{profile.nickname.slice(0,1)}}</div><div><h2>{{profile.nickname}}</h2><p>{{profile.email}}</p></div></div><div v-else class="notice">{{error||'正在读取资料...'}}</div><div class="shortcuts"><RouterLink to="/posts/">我的评论 <small>查看互动记录</small></RouterLink><RouterLink to="/posts/">我的收藏 <small>稍后继续阅读</small></RouterLink><RouterLink to="/posts/">我的点赞 <small>喜欢的内容</small></RouterLink></div></div></template>
<style scoped>.profile{max-width:900px;padding-top:75px}.page-title span{color:#8b79d6}.user-card{display:flex;align-items:center;gap:18px;margin:30px 0;padding:26px;border:1px solid #eae7f2;border-radius:18px;background:white}.avatar{width:58px;height:58px;display:grid;place-items:center;border-radius:19px;background:#efecff;color:#7767bc;font-size:28px}.user-card h2{margin:0 0 6px}.user-card p,.notice{color:#817d91;font-size:12px}.notice{margin:30px 0;padding:22px;border-radius:14px;background:#f5f3fc}.shortcuts{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}.shortcuts a{display:grid;gap:10px;padding:22px;border:1px solid #eae7f2;border-radius:16px;background:white;color:#6e5cbd;font-size:13px}.shortcuts small{color:#9993a7}@media(max-width:650px){.shortcuts{grid-template-columns:1fr}}</style>

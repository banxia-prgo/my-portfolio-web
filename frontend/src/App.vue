<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import SiteHeader from '@/components/SiteHeader.vue'
import SiteFooter from '@/components/SiteFooter.vue'
import SiteEnhancements from '@/components/SiteEnhancements.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

onMounted(() => {
  void auth.initialize()
})
</script>

<template>
  <div class="site-shell">
    <SiteHeader />
    <main class="site-main main"><RouterView /></main>
    <SiteFooter />
    <SiteEnhancements />
  </div>
</template>

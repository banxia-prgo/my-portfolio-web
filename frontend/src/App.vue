<script setup lang="ts">
import { RouterView } from 'vue-router'
import SiteHeader from '@/components/SiteHeader.vue'
import SiteFooter from '@/components/SiteFooter.vue'
import SiteEnhancements from '@/components/SiteEnhancements.vue'
</script>

<template>
  <div class="site-shell">
    <SiteHeader />
    <main class="site-main main"><RouterView /></main>
    <SiteFooter />
    <SiteEnhancements />
  </div>
</template>

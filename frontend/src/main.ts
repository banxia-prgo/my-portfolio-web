import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import './styles/main.css'
import './styles/original-site.css'
import './styles/vue-compat.css'
import './styles/typography-polish.css'
import './styles/homepage-refresh.css'
import './styles/site-design-system.css'

createApp(App).use(createPinia()).use(router).use(ElementPlus).mount('#app')

import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  resolve: { alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) } },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'https://api.banxia.xin',
        changeOrigin: true,
        secure: true,
      },
    },
  },
  build: { outDir: 'dist', sourcemap: false },
})

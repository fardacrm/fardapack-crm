import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  // ✅ تنظیمات پروکسی: این بخش جادویی است که مشکل اتصال را حل می‌کند
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000', // آدرس بک‌اند پایتون
        changeOrigin: true,
        secure: false,
      }
    }
  }
})
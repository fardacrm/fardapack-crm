<template>
  <AppLayout>
    <div class="page-content">
        <h2>{{ pageTitle }}</h2>
        <p>صفحه‌ای که به دنبال آن هستید وجود ندارد یا در دست توسعه است.</p>
        <router-link to="/" class="back-link">
          بازگشت به صفحه اصلی
        </router-link>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import AppLayout from '@/components/AppLayout.vue';
import { useRouter } from 'vue-router';

const pageTitle = ref('صفحه یافت نشد');
const router = useRouter();

onMounted(() => {
  // تشخیص صفحه بر اساس مسیر
  const path = router.currentRoute.value.path;
  if (path.includes('/companies')) pageTitle.value = '🏢 لیست شرکت‌ها';
  else if (path.includes('/calls')) pageTitle.value = '📞 لیست تماس‌ها';
  else if (path.includes('/followups')) pageTitle.value = '🗓️ لیست پیگیری‌ها';
  else if (path.includes('/orders')) pageTitle.value = '🛒 لیست سفارشات';
  else if (path.includes('/products')) pageTitle.value = '📦 مدیریت محصولات';
  else pageTitle.value = 'صفحه یافت نشد';
});
</script>

<style scoped>
.page-content {
    padding: 40px;
    text-align: center;
    font-family: Vazirmatn, sans-serif;
}

h2 {
    color: #e53e3e;
    margin-bottom: 20px;
}

p {
    color: #718096;
    margin-bottom: 30px;
    font-size: 16px;
}

.back-link {
    background-color: #4299e1;
    color: white;
    padding: 12px 24px;
    border-radius: 6px;
    text-decoration: none;
    transition: background-color 0.3s;
    display: inline-block;
}

.back-link:hover {
    background-color: #3182ce;
}
</style>
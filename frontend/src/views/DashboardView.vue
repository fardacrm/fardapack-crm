<template>
    <div class="page-content">
        <h2>نمای کلی سیستم</h2>
        <p>خوش آمدید. آمار کلی فعالیت‌ها به شرح زیر است:</p>
        
        <div v-if="loading" class="loading-message">
            در حال بارگذاری آمار...
        </div>
        
        <div v-if="error" class="error-detail">
            خطا در دریافت آمار: {{ error }}
        </div>
        
        <div v-if="stats" class="stats-grid">
            <div class="stat-card">
                <h3>تماس‌های امروز</h3>
                <p>{{ stats.calls_today }}</p>
            </div>
            <div class="stat-card">
                <h3>موفقِ امروز</h3>
                <p>{{ stats.calls_success_today }}</p>
            </div>
            <div class="stat-card">
                <h3>تماس‌های ۷ روز اخیر</h3>
                <p>{{ stats.last_7_days_calls }}</p>
            </div>
            <div class="stat-card danger"> <h3>پیگیری‌های عقب‌افتاده</h3>
                <p>{{ stats.overdue_followups }}</p>
            </div>
            <div class="stat-card neutral"> <h3>کل کاربران (من)</h3>
                <p>{{ stats.total_users }}</p>
            </div>
            <div class="stat-card neutral"> <h3>کل شرکت‌ها (سیستم)</h3>
                <p>{{ stats.total_companies }}</p>
            </div>
        </div>
        
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../api/index.js'; // 👈 ماژول API

const stats = ref(null);
const loading = ref(true);
const error = ref(null);

// 💡 [جدید] تابع واکشی آمار
const fetchDashboardStats = async () => {
    loading.value = true;
    error.value = null;
    try {
        const response = await api.get('/dashboard-stats');
        stats.value = response.data;
    } catch (err) {
        error.value = err.message || 'خطای ناشناس';
        console.error('Error fetching dashboard stats:', err);
    } finally {
        loading.value = false;
    }
};

onMounted(fetchDashboardStats);
</script>

<style scoped>
.page-content {
    padding: 20px;
}
.loading-message {
    text-align: center;
    padding: 30px;
    font-size: 1.2em;
    color: #555;
}
.error-detail {
    color: red;
    background-color: #ffe0e0;
    padding: 15px;
    border-radius: 5px;
}

/* 💡 [جدید] استایل کارت‌های آمار */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-top: 20px;
}
.stat-card {
    background-color: #007bff; /* آبی */
    color: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    text-align: center;
}
.stat-card h3 {
    margin: 0 0 10px 0;
    font-size: 1.1rem;
    font-weight: 600;
}
.stat-card p {
    margin: 0;
    font-size: 2.5rem;
    font-weight: 700;
}
/* کارت قرمز برای خطر */
.stat-card.danger {
    background-color: #dc3545;
}
/* کارت خاکستری برای آمار کلی */
.stat-card.neutral {
    background-color: #6c757d;
}
</style>
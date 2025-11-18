<template>
  <div class="page-content">
    <div v-if="loading" class="loading-message">در حال بارگذاری اطلاعات شرکت...</div>
    <div v-if="error" class="error-detail">{{ error }}</div>
    
    <div v-if="profileData">
      <div class="profile-header">
        <h2>پروفایل شرکت: {{ profileData.info.name }}</h2>
        <StatusBadge :text="profileData.info.status" />
      </div>
      
      <div class="info-grid">
        <div class="info-item"><strong>تلفن:</strong> {{ profileData.info.phone || '—' }}</div>
        <div class="info-item"><strong>سطح:</strong> {{ profileData.info.level }}</div>
        <div class="info-item"><strong>تاریخ ایجاد:</strong> {{ formatJalaliDateTime(profileData.info.created_at) }}</div>
        <div class="info-item"><strong>کارشناسان مرتبط:</strong> {{ profileData.info.experts || '—' }}</div>
      </div>
      <div class="info-item-full">
        <strong>آدرس:</strong> {{ profileData.info.address || '—' }}
      </div>
      <div class="info-item-full">
        <strong>یادداشت:</strong> {{ profileData.info.note || '—' }}
      </div>

      <div class="tabs">
        <button @click="activeTab = 'users'" :class="{ active: activeTab === 'users' }">
          کاربران ({{ profileData.users.length }})
        </button>
        <button @click="activeTab = 'calls'" :class="{ active: activeTab === 'calls' }">
          تماس‌ها ({{ profileData.calls.length }})
        </button>
        <button @click="activeTab = 'followups'" :class="{ active: activeTab === 'followups' }">
          پیگیری‌ها ({{ profileData.followups.length }})
        </button>
      </div>

      <div v-show="activeTab === 'users'" class="tab-content">
        <h3>کاربران مرتبط با این شرکت</h3>
        <table v-if="profileData.users.length > 0">
          <thead><tr><th>نام کامل</th><th>تلفن</th><th>سمت</th></tr></thead>
          <tbody>
            <tr v-for="user in profileData.users" :key="user.id">
              <td>{{ user.full_name }}</td>
              <td>{{ user.phone }}</td>
              <td>{{ user.role }}</td>
            </tr>
          </tbody>
        </table>
        <p v-else>هیچ کاربری برای این شرکت ثبت نشده است.</p>
      </div>

      <div v-show="activeTab === 'calls'" class="tab-content">
        <h3>تاریخچه تماس‌ها</h3>
        <table v-if="profileData.calls.length > 0">
          <thead><tr><th>تاریخ</th><th>وضعیت</th><th>توضیحات</th></tr></thead>
          <tbody>
            <tr v-for="call in profileData.calls" :key="call.id">
              <td>{{ formatJalaliDateTime(call.call_datetime) }}</td>
              <td><StatusBadge :text="call.status" /></td>
              <td>{{ call.description }}</td>
            </tr>
          </tbody>
        </table>
        <p v-else>هیچ تماسی ثبت نشده است.</p>
      </div>
      <div v-show="activeTab === 'followups'" class="tab-content">
        <h3>تاریخچه پیگیری‌ها</h3>
        <table v-if="profileData.followups.length > 0">
          <thead><tr><th>عنوان</th><th>تاریخ</th><th>وضعیت</th><th>جزئیات</th></tr></thead>
          <tbody>
            <tr v-for="task in profileData.followups" :key="task.id">
              <td>{{ task.title }}</td>
              <td>{{ formatJalaliDateTime(task.due_date) }}</td>
              <td><StatusBadge :text="task.status" /></td>
              <td>{{ task.details }}</td>
            </tr>
          </tbody>
        </table>
        <p v-else>هیچ پیگیری ثبت نشده است.</p>
      </div>
      
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import api from '../api/index.js';
import StatusBadge from '../components/StatusBadge.vue';
import { formatJalaliDateTime } from '../utils/formatters.js';

const route = useRoute();
const profileData = ref(null);
const loading = ref(true);
const error = ref(null);
const activeTab = ref('users'); // 👈 تب پیش‌فرض

const fetchCompanyProfile = async () => {
  loading.value = true;
  error.value = null;
  const companyId = route.params.id;

  try {
    const response = await api.get(`/companies/${companyId}/profile`);
    profileData.value = response.data;
  } catch (err) {
    error.value = err.message || 'خطا در واکشی پروفایل';
  } finally {
    loading.value = false;
  }
};

onMounted(fetchCompanyProfile);
</script>

<style scoped>
/* (استایل‌ها دقیقاً مشابه UserProfile است) */
.page-content { padding: 20px; }
table { width: 100%; border-collapse: collapse; margin-top: 20px; background-color: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
th, td { border: 1px solid #ddd; padding: 12px 15px; text-align: right; vertical-align: middle; }
th { background-color: #f2f2f2; font-weight: 700; color: #333; }
.loading-message { text-align: center; padding: 20px; color: #555; }
.error-detail { color: red; background-color: #ffe0e0; padding: 15px; border-radius: 5px; margin-top: 15px; }
.profile-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #eee; padding-bottom: 10px; }
.info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; background-color: #f9f9f9; padding: 20px; border-radius: 8px; margin-top: 20px; }
.info-item, .info-item-full { font-size: 1rem; }
.info-item-full { margin-top: 15px; background-color: #f9f9f9; padding: 20px; border-radius: 8px; }
.tabs { margin-top: 30px; border-bottom: 2px solid #ccc; }
.tabs button { padding: 10px 20px; border: none; background-color: transparent; font-family: 'Vazirmatn', sans-serif; font-size: 1.1rem; font-weight: 600; cursor: pointer; color: #555; border-radius: 6px 6px 0 0; }
.tabs button.active { background-color: white; border: 2px solid #ccc; border-bottom: 2px solid white; color: #007bff; position: relative; top: 2px; }
.tab-content { margin-top: 20px; }
</style>
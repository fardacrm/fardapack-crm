<template>
  <div class="page-content">
    <div v-if="loading" class="loading-message">در حال بارگذاری اطلاعات کاربر...</div>
    <div v-if="error" class="error-detail">{{ error }}</div>
    
    <div v-if="profileData">
      <div class="profile-header">
        <h2>پروفایل کاربر: {{ profileData.info.full_name }}</h2>
        <div class="header-actions">
          <button @click="openCallModal(profileData.info.id)" class="btn-action-call">📞 ثبت تماس</button>
          <button @click="openFollowupModal(profileData.info.id)" class="btn-action-followup">🗓️ ثبت پیگیری</button>
          <StatusBadge :text="profileData.info.status" />
        </div>
      </div>
      
      <div class="profile-card">
        <h3>اطلاعات پایه</h3>
        <div class="info-grid">
          <div class="info-item"><strong>📞 تلفن:</strong> <span>{{ profileData.info.phone || '—' }}</span></div>
          <div class="info-item"><strong>🏢 شرکت:</strong> <span>{{ profileData.info.company_name || '—' }}</span></div>
          <div class="info-item"><strong>🧑‍💼 سمت:</strong> <span>{{ profileData.info.role || '—' }}</span></div>
          <div class="info-item"><strong>📍 استان:</strong> <span>{{ profileData.info.province || '—' }}</span></div>
          <div class="info-item"><strong>🔧 حوزه فعالیت:</strong> <span>{{ profileData.info.domain || '—' }}</span></div>
          <div class="info-item"><strong>🌟 سطح:</strong> <span>{{ profileData.info.level }}</span></div>
          <div class="info-item"><strong>👤 کارشناس:</strong> <span>{{ profileData.info.sales_user || '—' }}</span></div>
          <div class="info-item"><strong>🗓️ تاریخ ایجاد:</strong> <span>{{ formatJalaliDateTime(profileData.info.created_at) }}</span></div>
        </div>
        <div class="info-item-full">
          <strong>📝 یادداشت:</strong>
          <p>{{ profileData.info.note || '—' }}</p>
        </div>
      </div>

      <div class="tabs">
        <button @click="activeTab = 'calls'" :class="{ active: activeTab === 'calls' }">
          تماس‌ها ({{ profileData.calls.length }})
        </button>
        <button @click="activeTab = 'followups'" :class="{ active: activeTab === 'followups' }">
          پیگیری‌ها ({{ profileData.followups.length }})
        </button>
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

    <CallFormModal
      v-if="showCallModal"
      :preselectedUserId="targetUserId"
      @close="closeCallModal"
      @save="handleCallSave"
    />
    <FollowupFormModal
      v-if="showFollowupModal"
      :preselectedUserId="targetUserId"
      @close="closeFollowupModal"
      @save="handleFollowupSave"
    />
    <div v-if="saveSuccess" class="global-success-message">عملیات با موفقیت انجام شد!</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import api from '../api/index.js';
import StatusBadge from '../components/StatusBadge.vue';
import { formatJalaliDateTime } from '../utils/formatters.js';
import CallFormModal from '../components/CallFormModal.vue';
import FollowupFormModal from '../components/FollowupFormModal.vue';

const route = useRoute();
const profileData = ref(null);
const loading = ref(true);
const error = ref(null);
const activeTab = ref('calls');
const saveSuccess = ref(false); 

const fetchUserProfile = async () => {
  loading.value = true;
  error.value = null;
  const userId = route.params.id;
  try {
    const response = await api.get(`/users/${userId}/profile`);
    profileData.value = response.data;
  } catch (err) {
    error.value = err.message || 'خطا در واکشی پروفایل';
  } finally {
    loading.value = false;
  }
};

// --- منطق مُدال‌ها ---
const showCallModal = ref(false);
const showFollowupModal = ref(false);
const targetUserId = ref(null); 

// 💡 [اصلاح] هر دو تابع اکنون ID را دریافت می‌کنند
const openCallModal = (userId) => {
  targetUserId.value = userId;
  showCallModal.value = true;
};
const closeCallModal = () => {
  showCallModal.value = false;
  targetUserId.value = null;
};
const openFollowupModal = (userId) => {
  targetUserId.value = userId;
  showFollowupModal.value = true;
};
const closeFollowupModal = () => {
  showFollowupModal.value = false;
  targetUserId.value = null;
};

// (بقیه توابع ذخیره‌سازی و واکشی بدون تغییر هستند)
const showSuccessMessage = () => {
  saveSuccess.value = true;
  setTimeout(() => { saveSuccess.value = false; }, 3000);
};
const handleCallSave = async (formData) => {
  error.value = null;
  try {
    await api.post('/calls', formData);
    closeCallModal();
    fetchUserProfile(); 
    showSuccessMessage();
  } catch (err) {
    error.value = 'خطا در ثبت تماس.';
    console.error('Error saving call:', err);
  }
};
const handleFollowupSave = async (formData) => {
  error.value = null;
  try {
    await api.post('/followups', formData);
    closeFollowupModal();
    fetchUserProfile(); 
    showSuccessMessage();
  } catch (err) {
    error.value = 'خطا در ثبت پیگیری.';
    console.error('Error saving followup:', err);
  }
};

onMounted(fetchUserProfile);
</script>

<style scoped>
/* (استایل‌ها بدون تغییر) */
.page-content { padding: 20px; }
table { width: 100%; border-collapse: collapse; margin-top: 20px; background-color: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
th, td { border: 1px solid #ddd; padding: 12px 15px; text-align: right; vertical-align: middle; }
th { background-color: #f2f2f2; font-weight: 700; color: #333; }
.loading-message { text-align: center; padding: 20px; color: #555; }
.error-detail { color: red; background-color: #ffe0e0; padding: 15px; border-radius: 5px; margin-top: 15px; }

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid #eee;
  padding-bottom: 15px;
  margin-bottom: 20px;
}
.profile-header h2 { margin: 0; }
.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}
.btn-action-call, .btn-action-followup {
  border: none;
  border-radius: 5px;
  padding: 10px 15px;
  font-family: 'Vazirmatn', sans-serif;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
}
.btn-action-call { background-color: #007bff; color: white; }
.btn-action-followup { background-color: #ffc107; color: #333; }
.profile-card {
  background-color: #ffffff;
  border-radius: 10px;
  padding: 25px;
  margin-top: 20px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  border: 1px solid #e0e0e0;
}
.profile-card h3 { margin-top: 0; border-bottom: 1px solid #f0f0f0; padding-bottom: 10px; margin-bottom: 20px; }
.info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px 25px; }
.info-item { font-size: 1rem; }
.info-item strong { color: #555; margin-left: 8px; }
.info-item span { color: #111; font-weight: 500; }
.info-item-full { margin-top: 20px; padding-top: 20px; border-top: 1px solid #f0f0f0; }
.info-item-full strong { display: block; color: #555; margin-bottom: 5px; }
.info-item-full p { margin: 0; color: #111; font-weight: 500; white-space: pre-wrap; }
.tabs { margin-top: 30px; border-bottom: 2px solid #ccc; }
.tabs button {
  padding: 10px 20px; border: none; background-color: transparent;
  font-family: 'Vazirmatn', sans-serif; font-size: 1.1rem;
  font-weight: 600; cursor: pointer; color: #555;
  border-radius: 6px 6px 0 0;
}
.tabs button.active {
  background-color: white; border: 2px solid #ccc; border-bottom: 2px solid white;
  color: #007bff; position: relative; top: 2px;
}
.tab-content { margin-top: 20px; }
.global-success-message {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background-color: #28a745;
  color: white;
  padding: 15px 30px;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
  z-index: 2000;
  font-weight: 600;
}
</style>
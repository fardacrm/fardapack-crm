<template>
    <div class="page-content">
        
        <div v-if="!isAdmin" class="loading-message">
            <p v-if="loadingUser">در حال بررسی مجوز دسترسی...</p>
            <p v-else class="error-detail">شما اجازه دسترسی به این صفحه را ندارید.</p>
        </div>

        <div v-if="isAdmin">
            <h2>🔒 مدیریت کاربران سیستم</h2>
            
            <div class="form-container">
                <h3>ایجاد کاربر ورود جدید</h3>
                <form @submit.prevent="handleCreateAppUser" class="add-user-form">
                    <input v-model="newUser.username" type="text" placeholder="نام کاربری جدید" required />
                    <input v-model="newUser.password" type="password" placeholder="رمز عبور" required />
                    <select v-model="newUser.role" required>
                        <option value="agent">کارشناس فروش</option>
                        <option value="admin">مدیر (Admin)</option>
                    </select>
                    <button type="submit" class="add-new-button">ایجاد کاربر</button>
                </form>
                <div v-if="saveSuccess" class="success-message">{{ successMessage }}</div>
                <div v-if="error" class="error-detail">{{ error }}</div>
            </div>

            <h3>لیست کاربران فعلی</h3>
            <div v-if="loadingUsers" class="loading-message">در حال بارگذاری لیست...</div>
            <table v-if="appUsers.length > 0">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>نام کاربری</th>
                        <th>نقش</th>
                        <th>تاریخ ایجاد</th>
                        <th>عملیات</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="user in appUsers" :key="user.id">
                        <td>{{ user.id }}</td>
                        <td>{{ user.username }}</td>
                        <td><StatusBadge :text="user.role === 'admin' ? 'مدیر' : 'کارشناس فروش'" /></td>
                        <td>{{ formatJalaliDateTime(user.created_at) }}</td>
                        <td>
                          <button @click="openPasswordModal(user)" class="btn-edit">🔑 تغییر رمز</button>
                          <button 
                            v-if="user.id !== currentUser.id" 
                            @click="handleDeleteAppUser(user.id, user.username)" 
                            class="btn-delete"
                          >
                            🗑️ حذف
                          </button>
                        </td>
                    </tr>
                </tbody>
            </table>

            <div class="backup-section">
              <h2>🛡️ پشتیبان‌گیری و بازیابی دیتابیس</h2>
              <p>
                از دیتابیس فعلی فایل بکاپ (crm.db) دریافت کنید یا یک فایل بکاپ قبلی را بازیابی کنید.
              </p>
              <div class="backup-actions">
                <button @click="handleDownloadBackup" class="btn-download">
                  ⬇️ دانلود بکاپ فعلی
                </button>
                <button @click="openRestoreModal" class="btn-restore">
                  ♻️ بازیابی از بکاپ
                </button>
              </div>
            </div>
        </div>

        <PasswordFormModal
            v-if="showPasswordModal && editingAppUser"
            :username="editingAppUser.username"
            @close="closePasswordModal"
            @save="handlePasswordSave"
        />
        
        <RestoreBackupModal
            v-if="showRestoreModal"
            @close="closeRestoreModal"
            @restore-success="handleRestoreSuccess"
        />
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../api/index.js'; 
import StatusBadge from '../components/StatusBadge.vue';
import PasswordFormModal from '../components/PasswordFormModal.vue';
import RestoreBackupModal from '../components/RestoreBackupModal.vue'; // 👈 [جدید]
import { formatJalaliDateTime } from '../utils/formatters.js';

const isAdmin = ref(false);
const loadingUser = ref(true);
const loadingUsers = ref(true);
const appUsers = ref([]);
const error = ref(null);
const saveSuccess = ref(false);
const successMessage = ref("");
const currentUser = ref(null);

const newUser = ref({
  username: '',
  password: '',
  role: 'agent'
});

// (منطق مودال رمز - بدون تغییر)
const showPasswordModal = ref(false);
const editingAppUser = ref(null);
const openPasswordModal = (user) => {
    editingAppUser.value = user;
    showPasswordModal.value = true;
};
const closePasswordModal = () => {
    showPasswordModal.value = false;
    editingAppUser.value = null;
};

// 💡 [جدید] منطق مودال بازیابی
const showRestoreModal = ref(false);
const openRestoreModal = () => { showRestoreModal.value = true; };
const closeRestoreModal = () => { showRestoreModal.value = false; };
const handleRestoreSuccess = () => {
  // پس از بازیابی، لیست کاربران و... را رفرش می‌کنیم
  fetchAppUsers();
  // (مُدال خودش پیغام موفقیت را نشان می‌دهد)
};

// (بررسی دسترسی ادمین - بدون تغییر)
const checkAdminAccess = async () => {
  loadingUser.value = true;
  try {
    const response = await api.get('/me');
    currentUser.value = response.data;
    if (response.data.role === 'admin') {
      isAdmin.value = true;
      await fetchAppUsers(); 
    } else {
      isAdmin.value = false;
    }
  } catch (err) {
    isAdmin.value = false;
    error.value = 'خطا در بررسی مجوز دسترسی.';
  } finally {
    loadingUser.value = false;
  }
};

// (واکشی کاربران - بدون تغییر)
const fetchAppUsers = async () => {
  loadingUsers.value = true;
  try {
    const response = await api.get('/admin/app-users');
    appUsers.value = response.data;
  } catch (err) {
    error.value = 'خطا در بارگذاری لیست کاربران.';
  } finally {
    loadingUsers.value = false;
  }
};

// (ایجاد کاربر - بدون تغییر)
const handleCreateAppUser = async () => {
  error.value = null;
  saveSuccess.value = false;
  try {
    const response = await api.post('/admin/app-users', newUser.value);
    successMessage.value = response.data.message;
    saveSuccess.value = true;
    newUser.value = { username: '', password: '', role: 'agent' };
    fetchAppUsers();
    setTimeout(() => { saveSuccess.value = false; }, 3000);
  } catch (err) {
    if (err.response && err.response.data && err.response.data.detail) {
      error.value = err.response.data.detail;
    } else {
      error.value = 'خطا در ایجاد کاربر.';
    }
  }
};

// (ذخیره رمز - بدون تغییر)
const handlePasswordSave = async (newPassword) => {
  error.value = null;
  saveSuccess.value = false;
  try {
    const response = await api.put(`/admin/app-users/${editingAppUser.value.id}/password`, {
      new_password: newPassword
    });
    successMessage.value = response.data.message;
    saveSuccess.value = true;
    closePasswordModal();
    setTimeout(() => { saveSuccess.value = false; }, 3000);
  } catch (err) {
     if (err.response && err.response.data && err.response.data.detail) {
      error.value = err.response.data.detail;
    } else {
      error.value = 'خطا در تغییر رمز عبور.';
    }
  }
};

// (حذف کاربر - بدون تغییر)
const handleDeleteAppUser = async (userId, username) => {
  if (!confirm(`آیا از حذف کاربر «${username}» مطمئن هستید؟ این عمل قابل بازگشت نیست.`)) {
    return;
  }
  error.value = null;
  saveSuccess.value = false;
  try {
    const response = await api.delete(`/admin/app-users/${userId}`);
    successMessage.value = response.data.message;
    saveSuccess.value = true;
    fetchAppUsers();
    setTimeout(() => { saveSuccess.value = false; }, 3000);
  } catch (err) {
    if (err.response && err.response.data && err.response.data.detail) {
      error.value = err.response.data.detail;
    } else {
      error.value = 'خطا در حذف کاربر.';
    }
  }
};

// 💡 [جدید] تابع دانلود بکاپ
const handleDownloadBackup = async () => {
  error.value = null;
  try {
    const response = await api.get('/admin/backup-db', {
      responseType: 'blob', // 👈 مهم: درخواست فایل
    });
    
    // ایجاد لینک موقت برای دانلود
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    const ts = new Date().toISOString().split('T')[0]; // تاریخ امروز
    link.setAttribute('download', `crm_backup_${ts}.db`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);

  } catch (err) {
    error.value = 'خطا در دانلود فایل بکاپ.';
  }
};

onMounted(checkAdminAccess);
</script>

<style scoped>
/* (استایل‌های قبلی) */
.page-content { padding: 20px; }
table { width: 100%; border-collapse: collapse; margin-top: 20px; background-color: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
th, td { border: 1px solid #ddd; padding: 12px 15px; text-align: right; vertical-align: middle; }
th { background-color: #f2f2f2; font-weight: 700; color: #333; }
.loading-message { text-align: center; padding: 20px; color: #555; }
.error-detail { color: red; background-color: #ffe0e0; padding: 15px; border-radius: 5px; margin-top: 15px; }
.success-message { color: green; background-color: #e6f7e6; padding: 15px; border-radius: 5px; margin-top: 15px; }
.form-container {
  background-color: #f9f9f9;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 30px;
}
.add-user-form { display: flex; flex-wrap: wrap; gap: 10px; }
.add-user-form input,
.add-user-form select {
  padding: 10px; border: 1px solid #ccc; border-radius: 5px;
  font-family: 'Vazirmatn', sans-serif; flex-grow: 1;
}
.add-new-button {
  background-color: #28a745; color: white; border: none;
  border-radius: 5px; padding: 10px 15px; font-family: 'Vazirmatn', sans-serif;
  font-size: 1rem; font-weight: 600; cursor: pointer;
}
td button {
  margin-left: 5px; border: none; padding: 5px 10px;
  border-radius: 5px; cursor: pointer; font-size: 0.9em;
}
.btn-edit { background-color: #ffc107; color: #333; }
.btn-delete { background-color: #dc3545; color: white; }

/* 💡 [جدید] استایل بخش بکاپ */
.backup-section {
  margin-top: 40px;
  padding: 20px;
  background-color: #fdfdfd;
  border: 1px solid #eee;
  border-radius: 8px;
}
.backup-section h2 {
  margin-top: 0;
}
.backup-actions {
  display: flex;
  gap: 15px;
  margin-top: 20px;
}
.btn-download, .btn-restore {
  border: none;
  border-radius: 5px;
  padding: 12px 20px;
  font-family: 'Vazirmatn', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
}
.btn-download {
  background-color: #007bff; /* آبی */
  color: white;
}
.btn-restore {
  background-color: #dc3545; /* قرمز */
  color: white;
}
</style>
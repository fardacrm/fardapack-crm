<template>
  <div class="modal-overlay" @click.self="close">
    <div class="modal-box">
      <h2>📥 ایمپورت اکسل مخاطبین</h2>
      
      <p class="help-text">
        ستون‌های الزامی: <strong>FirstName, Phone</strong><br>
        ستون‌های اختیاری: LastName, Role, Company, Status, Level, Domain, Province, OwnerUsername, Note
      </p>

      <div class="template-download">
        <button type="button" @click="downloadTemplate" class="btn-download-template">
          📦 دانلود الگوی اکسل
        </button>
      </div>

      <form @submit.prevent="handleUpload">
        <div class="input-group-full">
          <label for="excel_file">فایل اکسل (.xlsx) *</label>
          <input 
            id="excel_file" 
            type="file" 
            @change="onFileSelected" 
            accept=".xlsx"
            required 
            class="file-input"
          />
        </div>

        <div v-if="loading" class="loading-message">در حال آپلود و پردازش فایل... لطفا صبر کنید.</div>
        <div v-if="successMessage" class="success-message">{{ successMessage }}</div>
        <div v-if="error" class="error-detail">{{ error }}</div>
        <div v-if="importErrors.length > 0" class="error-list">
          <strong>خطاهای ردیف‌ها:</strong>
          <ul>
            <li v-for="(err, index) in importErrors" :key="index">{{ err }}</li>
          </ul>
        </div>
        
        <div class="modal-actions">
          <button type="button" class="btn-cancel" @click="close">بستن</button>
          <button type="submit" class="btn-save" :disabled="!selectedFile || loading">
            {{ loading ? 'در حال آپلود...' : 'شروع ایمپورت' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import api from '../api/index.js';

const emit = defineEmits(['close', 'import-success']);
const selectedFile = ref(null);
const loading = ref(false);
const error = ref(null);
const successMessage = ref(null);
const importErrors = ref([]);

const onFileSelected = (event) => {
  selectedFile.value = event.target.files[0];
};

const close = () => { emit('close'); };

// 💡 [جدید] تابع دانلود الگو
const downloadTemplate = async () => {
  try {
    const response = await api.get('/users/import-template', {
      responseType: 'blob', // 👈 مهم: به axios می‌گوییم که انتظار فایل داریم
    });
    
    // ایجاد یک لینک موقت در حافظه برای دانلود فایل
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'contacts_template.xlsx'); // نام فایل
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);

  } catch (err) {
    error.value = 'خطا در دانلود فایل الگو.';
  }
};

const handleUpload = async () => {
  if (!selectedFile.value) return;
  loading.value = true;
  error.value = null;
  successMessage.value = null;
  importErrors.value = [];
  
  const formData = new FormData();
  formData.append('file', selectedFile.value);

  try {
    const response = await api.post('/users/import-excel', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    
    successMessage.value = response.data.message;
    importErrors.value = response.data.errors;
    emit('import-success');

  } catch (err) {
    if (err.response && err.response.data && err.response.data.detail) {
      error.value = err.response.data.detail;
    } else {
      error.value = 'خطا در آپلود فایل.';
    }
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* (استایل‌های قبلی) */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.6); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-box { background-color: white; border-radius: 10px; padding: 25px; width: 90%; max-width: 600px; box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3); }
.modal-box h2 { margin-top: 0; margin-bottom: 20px; text-align: center; }
.input-group-full { margin-top: 15px; } 
.input-group-full label { margin-bottom: 5px; font-weight: 600; color: #333; display: block; }
.modal-actions { margin-top: 25px; display: flex; justify-content: flex-end; gap: 10px; }
.btn-save { background-color: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
.btn-cancel { background-color: #f0f0f0; color: #333; border: 1px solid #ccc; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
.help-text { font-size: 0.9em; background-color: #f9f9f9; padding: 10px; border-radius: 5px; border: 1px solid #eee; }
.file-input { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 5px; font-family: 'Vazirmatn', sans-serif; }
.loading-message { text-align: center; padding: 20px; color: #555; }
.error-detail { color: red; background-color: #ffe0e0; padding: 15px; border-radius: 5px; margin-top: 15px; }
.success-message { color: green; background-color: #e6f7e6; padding: 15px; border-radius: 5px; margin-top: 15px; }
.error-list { margin-top: 15px; padding: 10px; background-color: #fff3e0; border: 1px solid #ffe0b2; border-radius: 5px; max-height: 150px; overflow-y: auto; }
.error-list ul { padding-right: 20px; margin: 0; }

/* 💡 [جدید] استایل دکمه دانلود */
.template-download {
  margin-bottom: 20px;
  text-align: center;
}
.btn-download-template {
  background-color: #17a2b8; /* فیروزه‌ای */
  color: white;
  border: none;
  border-radius: 5px;
  padding: 10px 15px;
  font-family: 'Vazirmatn', sans-serif;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
}
</style>
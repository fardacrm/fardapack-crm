<template>
  <div class="modal-overlay" @click.self="close">
    <div class="modal-box">
      <h2>♻️ بازیابی از بکاپ</h2>
      
      <p class="help-text">
        توجه: فایل `.db` یا `.zip` (حاوی فایل `.db`) را آپلود کنید.
        <strong>این عمل، تمام دیتابیس فعلی را بازنویسی (Overwrite) می‌کند و قابل بازگشت نیست.</strong>
      </p>

      <form @submit.prevent="handleUpload">
        <div class="input-group-full">
          <label for="backup_file">فایل بکاپ (.db یا .zip) *</label>
          <input 
            id="backup_file" 
            type="file" 
            @change="onFileSelected" 
            accept=".db,.zip"
            required 
            class="file-input"
          />
        </div>

        <div v-if="loading" class="loading-message">در حال آپلود و بازیابی... این فرآیند ممکن است چند ثانیه طول بکشد.</div>
        <div v-if="successMessage" class="success-message">{{ successMessage }}</div>
        <div v-if="error" class="error-detail">{{ error }}</div>
        
        <div class="modal-actions">
          <button type="button" class="btn-cancel" @click="close">لغو</button>
          <button type="submit" class="btn-save btn-danger" :disabled="!selectedFile || loading">
            {{ loading ? 'در حال بازیابی...' : 'تایید و بازیابی' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import api from '../api/index.js';

const emit = defineEmits(['close', 'restore-success']);

const selectedFile = ref(null);
const loading = ref(false);
const error = ref(null);
const successMessage = ref(null);

const onFileSelected = (event) => {
  selectedFile.value = event.target.files[0];
};

const close = () => { emit('close'); };

// تابع آپلود فایل
const handleUpload = async () => {
  if (!selectedFile.value) return;

  loading.value = true;
  error.value = null;
  successMessage.value = null;
  
  const formData = new FormData();
  formData.append('file', selectedFile.value);

  try {
    const response = await api.post('/admin/restore-db', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    successMessage.value = response.data.message + " لطفاً برنامه را رفرش کنید.";
    emit('restore-success');

  } catch (err) {
    if (err.response && err.response.data && err.response.data.detail) {
      error.value = err.response.data.detail;
    } else {
      error.value = 'خطا در آپلود فایل بازیابی.';
    }
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* (استایل‌ها مشابه مودال‌های قبلی) */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.6); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-box { background-color: white; border-radius: 10px; padding: 25px; width: 90%; max-width: 600px; box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3); }
.modal-box h2 { margin-top: 0; margin-bottom: 20px; text-align: center; }
.input-group-full { margin-top: 15px; } 
.input-group-full label { margin-bottom: 5px; font-weight: 600; color: #333; display: block; }
.modal-actions { margin-top: 25px; display: flex; justify-content: flex-end; gap: 10px; }
.btn-save { background-color: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
.btn-cancel { background-color: #f0f0f0; color: #333; border: 1px solid #ccc; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
.help-text { font-size: 0.9em; background-color: #fef0e0; padding: 10px; border-radius: 5px; border: 1px solid #fee0b2; }
.help-text strong { color: #dc3545; }
.file-input { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 5px; font-family: 'Vazirmatn', sans-serif; }
.loading-message { text-align: center; padding: 20px; color: #555; }
.error-detail { color: red; background-color: #ffe0e0; padding: 15px; border-radius: 5px; margin-top: 15px; }
.success-message { color: green; background-color: #e6f7e6; padding: 15px; border-radius: 5px; margin-top: 15px; }
/* دکمه قرمز برای عملیات خطرناک */
.btn-danger {
  background-color: #dc3545;
}
</style>
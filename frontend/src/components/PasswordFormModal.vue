<template>
  <div class="modal-overlay" @click.self="close">
    <div class="modal-box">
      <h2>تغییر رمز عبور برای: {{ username }}</h2>

      <form @submit.prevent="submitForm">
        <div class="input-group-full">
          <label for="new_password">رمز عبور جدید *</label>
          <input 
            id="new_password" 
            v-model="newPassword" 
            type="password" 
            placeholder="حداقل 6 کاراکتر"
            required 
          />
        </div>

        <div class="modal-actions">
          <button type="button" class="btn-cancel" @click="close">لغو</button>
          <button type="submit" class="btn-save">ذخیره رمز</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

// نام کاربری را فقط برای نمایش دریافت می‌کند
const props = defineProps({
  username: { type: String, required: true }
});

const emit = defineEmits(['close', 'save']);
const newPassword = ref('');

const close = () => { emit('close'); };

const submitForm = () => {
  emit('save', newPassword.value);
};
</script>

<style scoped>
/* (استایل‌های مشابه مودال‌های قبلی) */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.6); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-box { background-color: white; border-radius: 10px; padding: 25px; width: 90%; max-width: 500px; box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3); }
.modal-box h2 { margin-top: 0; margin-bottom: 20px; text-align: center; }
.input-group-full { margin-top: 15px; } 
.input-group-full label { margin-bottom: 5px; font-weight: 600; color: #333; display: block; }
.input-group-full input { 
  padding: 10px; border: 1px solid #ccc; border-radius: 5px; font-family: 'Vazirmatn', sans-serif;
  box-sizing: border-box; width: 100%;
}
.modal-actions { margin-top: 25px; display: flex; justify-content: flex-end; gap: 10px; }
.btn-save { background-color: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
.btn-cancel { background-color: #f0f0f0; color: #333; border: 1px solid #ccc; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
</style>
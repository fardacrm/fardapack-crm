<template>
  <div class="modal-overlay" @click.self="close">
    <div class="modal-box">
      <h2>{{ isEditing ? 'ویرایش کاربر' : 'ایجاد کاربر جدید' }}</h2>
      
      <form @submit.prevent="submitForm">
        <div class="form-grid">
          
          <div class="input-group">
            <label for="first_name">نام *</label>
            <input id="first_name" v-model="formData.first_name" type="text" required />
          </div>
          
          <div class="input-group">
            <label for="last_name">نام خانوادگی</label>
            <input id="last_name" v-model="formData.last_name" type="text" />
          </div>

          <div class="input-group">
            <label for="phone">تلفن *</label>
            <input id="phone" v-model="formData.phone" type="tel" required />
          </div>

          <div class="input-group">
            <label for="company">شرکت (ID)</label>
            <input id="company" v-model="formData.company_id" type="number" placeholder="ID شرکت" />
          </div>

          <div class="input-group">
            <label for="status">وضعیت</label>
            <select id="status" v-model="formData.status">
              <option>بدون وضعیت</option>
              <option>در حال پیگیری</option>
              <option>پیش فاکتور</option>
              <option>مشتری شد</option>
              <option>لغو</option>
            </select>
          </div>

          <div class="input-group">
            <label for="level">سطح</label>
            <select id="level" v-model="formData.level">
              <option>هیچکدام</option>
              <option>طلایی</option>
              <option>نقره‌ای</option>
              <option>برنز</option>
            </select>
          </div>
        </div>
        
        <div class="modal-actions">
          <button type="button" class="btn-cancel" @click="close">لغو</button>
          <button type="submit" class="btn-save">ذخیره</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

// 💡 [تغییر] تعریف props برای دریافت داده‌های اولیه
const props = defineProps({
  initialData: {
    type: Object,
    default: null
  }
});

// 💡 [تغییر] تشخیص حالت ویرایش
const isEditing = ref(false);

// 💡 [تغییر] formData اکنون بر اساس initialData پر می‌شود
const formData = ref({
  first_name: '',
  last_name: '',
  phone: '',
  company_id: null,
  status: 'بدون وضعیت',
  level: 'هیچکدام'
});

// 💡 [جدید] تابعی که هنگام باز شدن مودال، فرم را پر می‌کند
onMounted(() => {
  if (props.initialData) {
    isEditing.value = true;
    // پر کردن فرم با داده‌های کاربر
    formData.value = {
      first_name: props.initialData.نام,
      last_name: props.initialData.نام_خانوادگی,
      phone: props.initialData.تلفن,
      // توجه: بک‌اند شما ID شرکت را برنمی‌گرداند، این بخش نیاز به تکمیل API دارد
      // فعلا company_id را null می‌گذاریم
      company_id: null, 
      status: props.initialData.وضعیت_کاربر || 'بدون وضعیت',
      level: props.initialData.سطح_کاربر || 'هیچکدام',
      // فیلدهای دیگر را هم در صورت نیاز اضافه کنید
    };
  }
});

const emit = defineEmits(['close', 'save']);
const close = () => { emit('close'); };

const submitForm = () => {
  // ارسال داده‌های فرم به کامپوننت والد
  emit('save', formData.value, isEditing.value ? props.initialData.ID : null);
};
</script>

<style scoped>
/* (استایل‌ها بدون تغییر باقی می‌مانند) */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.6); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-box { background-color: white; border-radius: 10px; padding: 25px; width: 90%; max-width: 600px; box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3); }
.modal-box h2 { margin-top: 0; margin-bottom: 20px; text-align: center; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
.input-group { display: flex; flex-direction: column; }
.input-group label { margin-bottom: 5px; font-weight: 600; color: #333; }
.input-group input, .input-group select { padding: 10px; border: 1px solid #ccc; border-radius: 5px; font-family: 'Vazirmatn', sans-serif; }
.modal-actions { margin-top: 25px; display: flex; justify-content: flex-end; gap: 10px; }
.btn-save { background-color: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
.btn-cancel { background-color: #f0f0f0; color: #333; border: 1px solid #ccc; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
</style>
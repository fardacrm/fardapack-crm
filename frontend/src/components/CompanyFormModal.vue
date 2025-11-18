<template>
  <div class="modal-overlay" @click.self="close">
    <div class="modal-box">
      <h2>{{ isEditing ? 'ویرایش شرکت' : 'ایجاد شرکت جدید' }}</h2>
      
      <form @submit.prevent="submitForm">
        <div class="form-grid">
          
          <div class="input-group">
            <label for="name">نام شرکت *</label>
            <input id="name" v-model="formData.name" type="text" required />
          </div>
          
          <div class="input-group">
            <label for="phone">تلفن</label>
            <input id="phone" v-model="formData.phone" type="tel" />
          </div>
        </div>

        <div class="input-group-full">
          <label for="address">آدرس</label>
          <input id="address" v-model="formData.address" type="text" />
        </div>

        <div class="form-grid">
          <div class="input-group">
            <label for="status">وضعیت</label>
            <select id="status" v-model="formData.status">
              <option>بدون وضعیت</option>
              <option>در حال پیگیری</option>
              <option>پیش فاکتور</option>
              <option>مشتری شد</option>
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

// تعریف props برای دریافت داده‌های اولیه (برای ویرایش)
const props = defineProps({
  initialData: {
    type: Object,
    default: null
  }
});

const isEditing = ref(false);

// مدل داده فرم
const formData = ref({
  name: '',
  phone: '',
  address: '',
  note: '', // نوت در فرم نیامد، اما در مدل وجود دارد
  level: 'هیچکدام',
  status: 'بدون وضعیت'
});

// پر کردن فرم در حالت ویرایش
onMounted(() => {
  if (props.initialData) {
    isEditing.value = true;
    formData.value = {
      name: props.initialData.نام_شرکت,
      phone: props.initialData.تلفن,
      address: props.initialData.address || '', // بک‌اند شما آدرس را برنمی‌گرداند
      note: props.initialData.note || '', // بک‌اند شما نوت را برنمی‌گرداند
      level: props.initialData.سطح_شرکت || 'هیچکدام',
      status: props.initialData.وضعیت_شرکت || 'بدون وضعیت',
    };
  }
});

const emit = defineEmits(['close', 'save']);
const close = () => { emit('close'); };

// ارسال داده‌ها به والد
const submitForm = () => {
  emit('save', formData.value, isEditing.value ? props.initialData.ID : null);
};
</script>

<style scoped>
/* استایل‌های مودال (مشابه UserFormModal) */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.6); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-box { background-color: white; border-radius: 10px; padding: 25px; width: 90%; max-width: 600px; box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3); }
.modal-box h2 { margin-top: 0; margin-bottom: 20px; text-align: center; }

/* 💡 استایل فرم تک ستونه و دو ستونه */
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
.input-group-full { margin-top: 15px; } 
.input-group { display: flex; flex-direction: column; margin-top: 15px; }

.input-group label, .input-group-full label { margin-bottom: 5px; font-weight: 600; color: #333; }
.input-group input, .input-group-full input, .input-group select { 
  padding: 10px; border: 1px solid #ccc; border-radius: 5px; font-family: 'Vazirmatn', sans-serif;
}
.modal-actions { margin-top: 25px; display: flex; justify-content: flex-end; gap: 10px; }
.btn-save { background-color: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
.btn-cancel { background-color: #f0f0f0; color: #333; border: 1px solid #ccc; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
</style>
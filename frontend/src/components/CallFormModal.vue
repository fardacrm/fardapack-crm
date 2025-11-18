<template>
  <div class="modal-overlay" @click.self="close">
    <div class="modal-box">
      <h2>ثبت تماس جدید</h2>
      
      <form @submit.prevent="submitForm">
        
        <div class="input-group-full">
          <label for="user_search">جستجوی کاربر (مخاطب) *</label>
          <input 
            id="user_search" 
            v-model="searchQuery" 
            type="text" 
            placeholder="نام، فامیل یا شرکت را تایپ کنید..."
            class="search-input"
            :disabled="isUserPreselected" 
          />
          <select id="user_id" v-model="formData.user_id" required :disabled="isUserPreselected">
            <option v-if="loadingUsers" value="">در حال بارگذاری...</option>
            <option v-else-if="filteredUsersList.length === 0" value="" disabled>کاربری یافت نشد</option>
            <option v-else v-for="user in filteredUsersList" :key="user.ID" :value="user.ID">
              {{ user.نام_کامل }} ({{ user.شرکت || 'بدون شرکت' }})
            </option>
          </select>
        </div>

        <div class="input-group-full">
          <label for="call_datetime">تاریخ و زمان تماس *</label>
          <date-picker
            id="call_datetime"
            v-model="formData.call_datetime"
            type="datetime"
            format="YYYY-MM-DD HH:mm:ss"
            display-format="jYYYY/jMM/jDD HH:mm"
            placeholder="تاریخ و زمان را انتخاب کنید"
            required
            class="custom-datepicker"
          />
        </div>

        <div class="input-group-full">
          <label for="status">وضعیت تماس *</label>
          <select id="status" v-model="formData.status" required>
            <option>موفق</option>
            <option>ناموفق</option>
            <option>خاموش</option>
            <option>رد تماس</option>
          </select>
        </div>

        <div class="input-group-full">
          <label for="description">توضیحات</label>
          <textarea id="description" v-model="formData.description" rows="3"></textarea>
        </div>
        
        <div class="modal-actions">
          <button type="button" class="btn-cancel" @click="close">لغو</button>
          <button type="submit" class="btn-save">ذخیره تماس</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import api from '../api/index.js';
// 💡💡💡 [اصلاح نهایی] ایمپورت از پکیج صحیح Vue 3 💡💡💡
import DatePicker from 'vue3-persian-datetime-picker';
import jMoment from 'moment-jalaali'; // (این را برای تبدیل زمان نیاز داریم)
// ❌ [حذف شد] ایمپورت CSS دستی حذف شد (پکیج جدید خودش لود می‌کند)

const props = defineProps({
  preselectedUserId: { type: Number, default: null }
});

const isUserPreselected = computed(() => props.preselectedUserId !== null);
const usersList = ref([]);
const loadingUsers = ref(true);
const searchQuery = ref("");

const filteredUsersList = computed(() => {
  if (!searchQuery.value) return usersList.value;
  const query = searchQuery.value.toLowerCase();
  return usersList.value.filter(user => 
    (user.نام_کامل && user.نام_کامل.toLowerCase().includes(query)) ||
    (user.شرکت && user.شرکت.toLowerCase().includes(query))
  );
});

// 💡 [اصلاح] مقدار اولیه اکنون یک رشته میلادی است که پکیج می‌فهمد
const getInitialGregorianDateTime = () => {
  const now = new Date();
  const pad = (num) => String(num).padStart(2, '0');
  // فرمت YYYY-MM-DD HH:mm:ss (میلادی)
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;
};

const formData = ref({
  user_id: null,
  call_datetime: getInitialGregorianDateTime(),
  status: 'موفق',
  description: ''
});

const fetchUsersForDropdown = async () => {
  loadingUsers.value = true;
  try {
    const response = await api.get('/users');
    usersList.value = response.data;
    if (props.preselectedUserId) {
      formData.value.user_id = props.preselectedUserId;
      const selectedUser = usersList.value.find(u => u.ID === props.preselectedUserId);
      if (selectedUser) {
        searchQuery.value = selectedUser.نام_کامل;
      }
    }
  } catch (error) { console.error('Error fetching users for modal:', error); }
  finally { loadingUsers.value = false; }
};

onMounted(fetchUsersForDropdown);

const emit = defineEmits(['close', 'save']);
const close = () => { emit('close'); };

const submitForm = () => {
  // 1. تاریخ (که اکنون میلادی است) را به آبجکت moment تبدیل می‌کنیم
  const momentDate = jMoment(formData.value.call_datetime, 'YYYY-MM-DD HH:mm:ss');
  // 2. آن را به فرمت ISO (میلادی) که FastAPI می‌فهمد تبدیل می‌کنیم
  const isoDateTime = momentDate.toISOString();

  const dataToSend = {
    user_id: parseInt(formData.value.user_id, 10),
    call_datetime: isoDateTime,
    status: formData.value.status,
    description: formData.value.description
  };
  emit('save', dataToSend);
};
</script>

<style scoped>
/* (استایل‌ها بدون تغییر) */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.6); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-box { background-color: white; border-radius: 10px; padding: 25px; width: 90%; max-width: 600px; box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3); }
.modal-box h2 { margin-top: 0; margin-bottom: 20px; text-align: center; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
.input-group-full { margin-top: 15px; } 
.input-group { display: flex; flex-direction: column; margin-top: 15px; }
.input-group label, .input-group-full label { margin-bottom: 5px; font-weight: 600; color: #333; }
.input-group input, .input-group-full input, .input-group-full select, .input-group select, .input-group-full textarea { 
  padding: 10px; border: 1px solid #ccc; border-radius: 5px; font-family: 'Vazirmatn', sans-serif;
  box-sizing: border-box; width: 100%;
}
.input-group-full select:disabled { background-color: #eee; }
.modal-actions { margin-top: 25px; display: flex; justify-content: flex-end; gap: 10px; }
.btn-save { background-color: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
.btn-cancel { background-color: #f0f0f0; color: #333; border: 1px solid #ccc; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
.search-input {
  margin-bottom: 8px; width: 100%; box-sizing: border-box; padding: 10px;
  border: 1px solid #ccc; border-radius: 5px; font-family: 'Vazirmatn', sans-serif;
}
/* استایل برای تقویم */
.custom-datepicker { width: 100%; }
.custom-datepicker :deep(input) {
  width: 100%; box-sizing: border-box; padding: 10px;
  border: 1px solid #ccc; border-radius: 5px;
  font-family: 'Vazirmatn', sans-serif;
  cursor: pointer;
}
</style>
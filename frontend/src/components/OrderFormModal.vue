<template>
  <div class="modal-overlay" @click.self="close">
    <div class="modal-box">
      <h2>{{ isEditing ? 'ویرایش سفارش' : 'ثبت سفارش جدید' }}</h2>
      
      <form @submit.prevent="submitForm">
        
        <div class="input-group-full">
          <label>سفارش برای:</label>
          <div class="radio-group">
            <label><input type="radio" v-model="orderType" value="user"> کاربر</label>
            <label><input type="radio" v-model="orderType" value="company"> شرکت</label>
          </div>
        </div>

        <div v-if="orderType === 'user'" class="input-group-full">
          <label for="user_search">کاربر (مخاطب) *</label>
          <input 
            id="user_search" 
            v-model="searchQueryUser" 
            type="text" 
            placeholder="جستجوی نام کاربر..."
            class="search-input"
          />
          <select id="user_id" v-model="formData.user_id" required>
            <option v-if="loading.users" value="">در حال بارگذاری...</option>
            <option v-else-if="filteredUsersList.length === 0" value="" disabled>کاربری یافت نشد</option>
            <option v-else v-for="user in filteredUsersList" :key="user.ID" :value="user.ID">
              {{ user.نام_کامل }} ({{ user.شرکت || 'بدون شرکت' }})
            </option>
          </select>
        </div>
        
        <div v-if="orderType === 'company'" class="input-group-full">
          <label for="company_search">شرکت *</label>
           <input 
            id="company_search" 
            v-model="searchQueryCompany" 
            type="text" 
            placeholder="جستجوی نام شرکت..."
            class="search-input"
          />
          <select id="company_id" v-model="formData.company_id" required>
            <option v-if="loading.companies" value="">در حال بارگذاری...</option>
            <option v-else-if="filteredCompaniesList.length === 0" value="" disabled>شرکتی یافت نشد</option>
            <option v-else v-for="company in filteredCompaniesList" :key="company.ID" :value="company.ID">
              {{ company.نام_شرکت }}
            </option>
          </select>
        </div>

        <div class="input-group-full">
          <label for="product_search">محصول *</label>
          <input 
            id="product_search" 
            v-model="searchQueryProduct" 
            type="text" 
            placeholder="جستجوی نام محصول..."
            class="search-input"
          />
          <select id="product_id" v-model="formData.product_id" required>
            <option v-if="loading.products" value="">در حال بارگذاری...</option>
            <option v-else-if="filteredProductsList.length === 0" value="" disabled>محصولی یافت نشد</option>
            <option v-else v-for="product in filteredProductsList" :key="product.id" :value="product.id">
              {{ product.name }} ({{ product.category }})
            </option>
          </select>
        </div>

        <div class="form-grid">
          <div class="input-group">
            <label for="order_date">تاریخ سفارش *</label>
            <date-picker
              id="order_date"
              v-model="formData.order_date"
              format="YYYY-MM-DD"
              display-format="jYYYY/jMM/jDD"
              required
              class="custom-datepicker"
            />
          </div>
          <div class="input-group">
            <label for="total_amount">مبلغ کل *</label>
            <input id="total_amount" v-model.number="formData.total_amount" type="number" min="0" required />
          </div>
        </div>
        <div class="input-group-full">
          <label for="status">وضعیت سفارش *</label>
          <select id="status" v-model="formData.status" required>
            <option>در حال پیگیری</option>
            <option>تایید شده</option>
            <option>کنسل شده</option>
            <option>رد شده</option>
          </select>
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
import { ref, onMounted, watch, computed } from 'vue';
import api from '../api/index.js';
// ❌ [حذف شد] vSelect
import DatePicker from 'vue3-persian-datetime-picker';

// ❌ [حذف شد] CSS پکیج v-select

// Props
const props = defineProps({
  initialData: { type: Object, default: null }
});

const emit = defineEmits(['close', 'save']);
const isEditing = ref(false);

// --- مدیریت داده‌های فرم ---
const formData = ref({
  user_id: null,
  company_id: null,
  product_id: null,
  order_date: new Date().toISOString().split('T')[0],
  status: 'در حال پیگیری',
  total_amount: 0
});

// --- مدیریت دراپ‌داون‌ها ---
const orderType = ref('user');
const usersList = ref([]);
const companiesList = ref([]);
const productsList = ref([]);
const loading = ref({
  users: false,
  companies: false,
  products: false
});

// 💡 [جدید] متغیرهای جستجو
const searchQueryUser = ref("");
const searchQueryCompany = ref("");
const searchQueryProduct = ref("");

// 💡 [جدید] لیست‌های فیلتر شده
const filteredUsersList = computed(() => {
  const query = searchQueryUser.value.toLowerCase();
  if (!query) return usersList.value;
  return usersList.value.filter(u => u.نام_کامل.toLowerCase().includes(query));
});
const filteredCompaniesList = computed(() => {
  const query = searchQueryCompany.value.toLowerCase();
  if (!query) return companiesList.value;
  return companiesList.value.filter(c => c.نام_شرکت.toLowerCase().includes(query));
});
const filteredProductsList = computed(() => {
  const query = searchQueryProduct.value.toLowerCase();
  if (!query) return productsList.value;
  return productsList.value.filter(p => p.name.toLowerCase().includes(query) || p.category.toLowerCase().includes(query));
});

// --- واکشی داده‌ها ---
const fetchData = async (type, endpoint, listRef) => {
  loading.value[type] = true;
  try {
    const response = await api.get(endpoint);
    listRef.value = response.data;
  } catch (error) {
    console.error(`Error fetching ${type}:`, error);
  } finally {
    loading.value[type] = false;
  }
};

onMounted(() => {
  fetchData('users', '/users', usersList);
  fetchData('companies', '/companies', companiesList);
  fetchData('products', '/products', productsList);

  if (props.initialData) {
    isEditing.value = true;
    formData.value = {
      user_id: props.initialData.user_id,
      company_id: props.initialData.company_id,
      product_id: props.initialData.product_id,
      order_date: props.initialData.تاریخ_سفارش, // 💡 [اصلاح] استفاده از نام فیلد صحیح
      status: props.initialData.وضعیت,
      total_amount: parseFloat(String(props.initialData.مبلغ_کل).replace(/,/g, '')) || 0,
    };
    if (props.initialData.company_id) {
      orderType.value = 'company';
    } else {
      orderType.value = 'user';
    }
  }
});

// --- منطق فرم ---
watch(orderType, (newType) => {
  if (newType === 'user') {
    formData.value.company_id = null;
  } else {
    formData.value.user_id = null;
  }
});

const close = () => { emit('close'); };

const submitForm = () => {
  // 💡 [اصلاح] پاکسازی IDها قبل از ارسال
  const dataToSend = { ...formData.value };
  dataToSend.user_id = dataToSend.user_id ? parseInt(dataToSend.user_id, 10) : null;
  dataToSend.company_id = dataToSend.company_id ? parseInt(dataToSend.company_id, 10) : null;
  dataToSend.product_id = parseInt(dataToSend.product_id, 10);
  
  emit('save', dataToSend, isEditing.value ? props.initialData.ID : null);
};
</script>

<style scoped>
/* (استایل‌ها مشابه مودال‌های قبلی) */
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
.modal-actions { margin-top: 25px; display: flex; justify-content: flex-end; gap: 10px; }
.btn-save { background-color: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
.btn-cancel { background-color: #f0f0f0; color: #333; border: 1px solid #ccc; padding: 10px 20px; border-radius: 5px; cursor: pointer; }

.radio-group {
  display: flex; gap: 20px; border: 1px solid #ccc;
  border-radius: 5px; padding: 10px;
}
.radio-group label { display: flex; align-items: center; gap: 5px; margin-bottom: 0; }

/* 💡 [جدید] استایل برای فیلدهای جستجو */
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
<template>
    <div class="page-content">
        
        <div class="page-header">
            <h2>🛒 لیست سفارشات</h2>
            <button @click="openModal()" class="add-new-button">+ ثبت سفارش جدید</button>
        </div>
        
        <!-- ✅ استفاده از کامپوننت استاندارد AppFilter -->
        <AppFilter @filter="fetchOrders" @reset="resetFilters">
            <template #inputs>
                <!-- فیلتر کاربر -->
                <div class="filter-item">
                    <span class="icon">👤</span>
                    <Multiselect
                        v-model="filters.user_filter"
                        placeholder="انتخاب کاربر"
                        :options="dropdowns.users"
                        :searchable="true"
                        :loading="loading.users"
                        class="multiselect-filter"
                    />
                </div>
                
                <!-- فیلتر شرکت -->
                <div class="filter-item">
                    <span class="icon">🏢</span>
                    <Multiselect
                        v-model="filters.company_filter"
                        placeholder="انتخاب شرکت"
                        :options="dropdowns.companies"
                        :searchable="true"
                        :loading="loading.companies"
                        class="multiselect-filter"
                    />
                </div>

                <!-- فیلتر محصول -->
                <div class="filter-item">
                    <span class="icon">📦</span>
                    <Multiselect
                        v-model="filters.product_filter"
                        placeholder="انتخاب محصول"
                        :options="dropdowns.products"
                        :searchable="true"
                        :loading="loading.products"
                        class="multiselect-filter"
                    />
                </div>

                <!-- فیلتر وضعیت -->
                <div class="filter-item">
                    <span class="icon">📊</span>
                    <Multiselect
                        v-model="filters.status_filter"
                        placeholder="انتخاب وضعیت"
                        :options="ORDER_STATUSES"
                        class="multiselect-filter"
                    />
                </div>
            </template>
        </AppFilter>

        <div v-if="loading.orders" class="loading-message">در حال بارگذاری اطلاعات سفارشات...</div>
        <div v-show="error" class="error-detail">خطا: {{ error }}</div>
        <div v-if="saveSuccess" class="success-message">عملیات با موفقیت انجام شد!</div>
        
        <table v-if="orders.length > 0 && !loading.orders">
            <thead>
                <tr>
                    <th>مشتری (کاربر/شرکت)</th>
                    <th>محصول</th>
                    <th>تاریخ سفارش</th>
                    <th>مبلغ کل</th>
                    <th>وضعیت</th>
                    <th>عملیات</th>
                </tr>
            </thead>
            <tbody>
                <!-- نمایش ردیف‌های برش‌خورده (Pagination سمت کلاینت) -->
                <tr v-for="order in currentOrders" :key="order.ID">
                    <td>{{ order.کاربر !== '—' ? order.کاربر : order.شرکت }}</td>
                    <td>{{ order.محصول }} ({{ order.دسته_بندی }})</td>
                    <td>{{ formatJalaliDate(order.تاریخ_سفارش) }}</td>
                    <td>{{ order.مبلغ_کل }}</td>
                    <td><StatusBadge :text="order.وضعیت" /></td>
                    <td>
                      <button @click="openModal(order)" class="btn-edit">✏️ ویرایش</button>
                    </td>
                </tr>
            </tbody>
        </table>
        
        <!-- ✅ کامپوننت TableFooter با مقادیر Pagination -->
        <TableFooter
            v-if="!loading.orders && totalRecords > 0"
            :total-records="totalRecords"
            :page-size="pageSize"
            :current-page="currentPage"
            @update:pageSize="updatePageSize"
            @goToPage="goToPage"
        />

        <p v-if="orders.length === 0 && !loading.orders" class="loading-message">
            سفارشی یافت نشد.
        </p>
    </div>
    
    <OrderFormModal
      v-if="showModal"
      :initialData="editingOrder"
      @close="closeModal"
      @save="handleSave"
    />
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'; // ✅ اضافه شدن computed
import api from '../api/index.js';
import AppFilter from '../components/AppFilter.vue'; 
import TableFooter from '../components/TableFooter.vue'; // ✅ ایمپورت جدید
import StatusBadge from '../components/StatusBadge.vue';
import OrderFormModal from '../components/OrderFormModal.vue';
import { formatJalaliDate } from '../utils/formatters.js';
import Multiselect from '@vueform/multiselect';
import '@vueform/multiselect/themes/default.css';

const ORDER_STATUSES = ["در حال پیگیری", "تایید شده", "کنسل شده", "رد شده"];

const orders = ref([]);
const error = ref(null);
const saveSuccess = ref(false);
const showModal = ref(false);
const editingOrder = ref(null);

// ✅ وضعیت‌های Pagination
const totalRecords = ref(0); 
const pageSize = ref(20); 
const currentPage = ref(1); 

const filters = ref({
  user_filter: null,
  company_filter: null,
  product_filter: null,
  status_filter: null
});

const loading = ref({
  orders: true,
  users: false,
  companies: false,
  products: false
});
const dropdowns = ref({
  users: [],
  companies: [],
  products: []
});

// --- منطق Pagination در سمت کلاینت ---
const currentOrders = computed(() => {
    if (pageSize.value === 'all') {
        return orders.value;
    }
    const limit = parseInt(pageSize.value);
    const start = (currentPage.value - 1) * limit;
    const end = start + limit;
    return orders.value.slice(start, end);
});

const updatePageSize = (newSize) => {
    pageSize.value = newSize === 'all' ? 'all' : parseInt(newSize);
    currentPage.value = 1; 
};

const goToPage = (page) => {
    const limit = parseInt(pageSize.value);
    const totalPages = Math.ceil(totalRecords.value / limit);
    if (page >= 1 && page <= totalPages) {
        currentPage.value = page;
    }
};
// --- پایان منطق Pagination ---


// --- منطق مودال و ذخیره (بدون تغییر) ---
const openModal = (order = null) => {
  editingOrder.value = order;
  showModal.value = true;
};
const closeModal = () => {
  showModal.value = false;
  editingOrder.value = null;
};
const handleSave = async (formData, orderId) => {
  error.value = null; saveSuccess.value = false;
  const dataToSend = { ...formData };
  try {
    if (orderId) { await api.put(`/orders/${orderId}`, dataToSend); } 
    else { await api.post('/orders', dataToSend); }
    saveSuccess.value = true;
    closeModal();
    fetchOrders();
    setTimeout(() => { saveSuccess.value = false; }, 3000);
  } catch (err) {
    if (err.response && err.response.data && err.response.data.detail) {
      error.value = err.response.data.detail;
    } else { error.value = 'خطا در ذخیره سفارش.'; }
  }
};

// (تابع واکشی)
const fetchOrders = async () => {
    loading.value.orders = true;
    error.value = null;

    const params = {};
    if (filters.value.user_filter) params.user_filter = filters.value.user_filter;
    if (filters.value.company_filter) params.company_filter = filters.value.company_filter;
    if (filters.value.product_filter) params.product_filter = filters.value.product_filter;
    if (filters.value.status_filter) params.status_filter = filters.value.status_filter;

    try {
        const response = await api.get('/orders', { params: params });
        const data = response.data.data || response.data;

        orders.value = data;
        totalRecords.value = data.length; // ✅ آپدیت totalRecords

        const limit = parseInt(pageSize.value);
        const totalPages = Math.ceil(totalRecords.value / limit);
        if (currentPage.value > totalPages) {
            currentPage.value = totalPages > 0 ? totalPages : 1;
        }

    } catch (err) {
        error.value = err.message || 'خطای ناشناس';
        orders.value = [];
        totalRecords.value = 0;
    } finally {
        loading.value.orders = false;
    }
};

// واکشی داده‌های دراپ‌داون
const fetchDropdownData = async () => {
  loading.value.users = true;
  loading.value.companies = true;
  loading.value.products = true;
  
  try {
    const [usersRes, companiesRes, productsRes] = await Promise.all([
      api.get('/users'),
      api.get('/companies'),
      api.get('/products')
    ]);
    
    dropdowns.value.users = usersRes.data.map(u => ({ value: u.ID, label: u.نام_کامل }));
    dropdowns.value.companies = companiesRes.data.map(c => ({ value: c.ID, label: c.نام_شرکت }));
    dropdowns.value.products = productsRes.data.map(p => ({ value: p.id, label: `${p.name} (${p.category})` }));

  } catch (err) {
    error.value = "خطا در بارگذاری داده‌های فیلتر";
  } finally {
    loading.value.users = false;
    loading.value.companies = false;
    loading.value.products = false;
  }
};

const resetFilters = () => {
  filters.value = { user_filter: null, company_filter: null, product_filter: null, status_filter: null };
  currentPage.value = 1;
  fetchOrders(); // بعد از ریست، دوباره لیست را بگیر
};

onMounted(() => {
  fetchOrders();
  fetchDropdownData();
});
</script>

<style scoped>
.page-content { 
  padding: 20px; max-width: 1400px; margin: 20px auto; 
  background-color: #ffffff; border-radius: 10px; 
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); border: 1px solid #e0e0e0;
}
table { width: 100%; border-collapse: collapse; margin-top: 20px; background-color: white; }
th, td { border: 1px solid #ddd; padding: 12px 15px; text-align: right; vertical-align: middle; }
th { background-color: #f2f2f2; font-weight: 700; color: #333; }
.loading-message { text-align: center; padding: 20px; color: #555; }
.error-detail { color: red; background-color: #ffe0e0; padding: 15px; border-radius: 5px; margin-top: 15px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.add-new-button { background-color: #28a745; color: white; border: none; border-radius: 5px; padding: 10px 15px; font-family: 'Vazirmatn', sans-serif; font-size: 1rem; font-weight: 600; cursor: pointer; }
.success-message { color: green; background-color: #e6f7e6; padding: 15px; border-radius: 5px; margin-top: 15px; }
.btn-edit { background-color: #ffc107; color: #333; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer; font-size: 0.9em; }
/* ✅ table-footer قدیمی حذف شد و توسط کامپوننت جایگزین شد */
/* .table-footer { ... } */

/* ✅ استایل‌های یکپارچه فیلتر (کپی شده از سایر صفحات) */
.filter-item {
  position: relative;
  flex: 1;
  min-width: 200px;
}

.filter-item .icon {
  position: absolute;
  top: 50%;
  right: 12px;
  transform: translateY(-50%);
  color: #888;
  z-index: 1;
}

input[type="text"],
:deep(.multiselect-filter) {
  width: 100%;
  box-sizing: border-box; 
  padding: 10px 35px 10px 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  font-family: 'Vazirmatn', sans-serif;
  color: #333;
  height: 44px;
}

:deep(.multiselect-filter) {
  --ms-padding-left: 10px;
  --ms-padding-right: 35px; 
  --ms-min-height: 44px; 
  --ms-font-family: 'Vazirmatn', sans-serif;
  --ms-border-color: #ccc;
  --ms-radius: 5px;
  --ms-tag-bg: #007bff;
  --ms-tag-color: white;
}
</style>
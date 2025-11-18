<template>
    <div class="page-content">
        
        <div class="page-header">
            <h2>🏢 لیست شرکت‌ها</h2>
            <button @click="openModal()" class="add-new-button">+ افزودن شرکت جدید</button>
        </div>
        
        <!-- ✅ استفاده از کامپوننت استاندارد AppFilter -->
        <AppFilter @filter="fetchCompanies" @reset="resetFilters">
            <template #inputs>
                <!-- فیلتر نام شرکت -->
                <div class="filter-item">
                    <span class="icon">🏢</span>
                    <input 
                        v-model="filters.q_name" 
                        type="text" 
                        placeholder="جستجوی نام شرکت..."
                    />
                </div>

                <!-- فیلتر وضعیت‌ها -->
                <div class="filter-item">
                    <span class="icon">📊</span>
                    <Multiselect
                        v-model="filters.f_status"
                        mode="tags"
                        placeholder="انتخاب وضعیت‌ها"
                        :options="COMPANY_STATUSES"
                        :close-on-select="false"
                        class="multiselect-filter"
                    />
                </div>

                <!-- فیلتر سطح‌ها -->
                <div class="filter-item">
                    <span class="icon">🌟</span>
                    <Multiselect
                        v-model="filters.f_level"
                        mode="tags"
                        placeholder="انتخاب سطح‌ها"
                        :options="LEVELS"
                        :close-on-select="false"
                        class="multiselect-filter"
                    />
                </div>
            </template>
        </AppFilter>

        <div v-if="loading" class="loading-message">در حال بارگذاری اطلاعات شرکت‌ها...</div>
        <div v-show="error" class="error-detail">خطا: {{ error }}</div>
        <div v-if="saveSuccess" class="success-message">عملیات با موفقیت انجام شد!</div>
        
        <table v-if="companies.length > 0 && !loading">
            <thead>
                <tr>
                    <th>نام شرکت</th>
                    <th>تلفن</th>
                    <th>وضعیت</th>
                    <th>سطح</th>
                    <th>کارشناس</th>
                    <th>پیگیری باز</th>
                </tr>
            </thead>
            <tbody>
                <!-- نمایش ردیف‌های برش‌خورده (Pagination سمت کلاینت) -->
                <tr v-for="company in currentCompanies" :key="company.ID">
                    <td class="name-cell">
                        <span>{{ company.نام_شرکت }}</span>
                        <div class="context-menu">
                            <button @click="viewCompanyProfile(company.ID)">👁 نمایش پروفایل</button>
                            <button @click="openModal(company)">✏️ ویرایش</button>
                        </div>
                    </td>
                    <td>{{ company.تلفن }}</td>
                    <td><StatusBadge :text="company.وضعیت_شرکت" /></td>
                    <td><StatusBadge :text="company.سطح_شرکت" /></td>
                    <td>{{ company.کارشناس_فروش }}</td>
                    <td><StatusBadge :text="company.پیگیری_باز_دارد" /></td>
                </tr>
            </tbody>
        </table>
        
        <!-- ✅ کامپوننت TableFooter با مقادیر Pagination -->
        <TableFooter
            v-if="!loading && totalRecords > 0"
            :total-records="totalRecords"
            :page-size="pageSize"
            :current-page="currentPage"
            @update:pageSize="updatePageSize"
            @goToPage="goToPage"
        />

        <p v-if="companies.length === 0 && !loading" class="loading-message">
            شرکتی یافت نشد.
        </p>
    </div>
    
    <CompanyFormModal
      v-if="showModal"
      :initialData="editingCompany"
      @close="closeModal"
      @save="handleSave"
    />
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'; // ✅ اضافه شدن computed
import { useRouter } from 'vue-router';
import api from '../api/index.js';
import AppFilter from '../components/AppFilter.vue'; 
import TableFooter from '../components/TableFooter.vue'; // ✅ ایمپورت جدید
import StatusBadge from '../components/StatusBadge.vue';
import CompanyFormModal from '../components/CompanyFormModal.vue';
import Multiselect from '@vueform/multiselect';
import '@vueform/multiselect/themes/default.css';

const router = useRouter();
const COMPANY_STATUSES = ["بدون وضعیت", "در حال پیگیری", "پیش فاکتور", "مشتری شد"];
const LEVELS = ["هیچکدام", "طلایی", "نقره‌ای", "برنز"];

const companies = ref([]);
const loading = ref(true);
const error = ref(null);
const saveSuccess = ref(false);
const showModal = ref(false);
const editingCompany = ref(null);

// ✅ وضعیت‌های Pagination
const totalRecords = ref(0); 
const pageSize = ref(20); 
const currentPage = ref(1); 

const filters = ref({
  q_name: '',
  f_status: [],
  f_level: []
});

// --- منطق Pagination در سمت کلاینت ---
const currentCompanies = computed(() => {
    if (pageSize.value === 'all') {
        return companies.value;
    }
    const limit = parseInt(pageSize.value);
    const start = (currentPage.value - 1) * limit;
    const end = start + limit;
    return companies.value.slice(start, end);
});

const updatePageSize = (newSize) => {
    pageSize.value = newSize === 'all' ? 'all' : parseInt(newSize);
    currentPage.value = 1; // ریست به صفحه اول
};

const goToPage = (page) => {
    const limit = parseInt(pageSize.value);
    const totalPages = Math.ceil(totalRecords.value / limit);
    if (page >= 1 && page <= totalPages) {
        currentPage.value = page;
    }
};
// --- پایان منطق Pagination ---


// (منطق مودال و ذخیره بدون تغییر)
const openModal = (company = null) => {
  editingCompany.value = company;
  showModal.value = true;
};
const closeModal = () => {
  showModal.value = false;
  editingCompany.value = null;
};
const handleSave = async (formData, companyId) => {
  error.value = null;
  saveSuccess.value = false;
  const dataToSend = { ...formData };
  try {
    if (companyId) {
      await api.put(`/companies/${companyId}`, dataToSend);
    } else {
      await api.post('/companies', dataToSend);
    }
    saveSuccess.value = true;
    closeModal();
    fetchCompanies();
    setTimeout(() => { saveSuccess.value = false; }, 3000);
  } catch (err) {
    if (err.response && err.response.data && err.response.data.detail) {
      error.value = err.response.data.detail;
    } else {
      error.value = 'خطا در ذخیره شرکت.';
    }
    console.error('Error saving company:', err);
  }
};

// (تابع واکشی)
const fetchCompanies = async () => {
    loading.value = true;
    error.value = null;
    const params = new URLSearchParams();
    if (filters.value.q_name) params.append('q_name', filters.value.q_name);
    filters.value.f_status.forEach(status => {
      params.append('f_status', status);
    });
    filters.value.f_level.forEach(level => {
      params.append('f_level', level);
    });
    try {
        const response = await api.get('/companies', { params: params });
        const data = response.data.data || response.data;

        companies.value = data;
        totalRecords.value = data.length; // ✅ آپدیت totalRecords

        // اطمینان از ماندن در صفحه صحیح پس از فیلتر
        const limit = parseInt(pageSize.value);
        const totalPages = Math.ceil(totalRecords.value / limit);
        if (currentPage.value > totalPages) {
            currentPage.value = totalPages > 0 ? totalPages : 1;
        }

    } catch (err) {
        error.value = err.message || 'خطای ناشناس';
    } finally {
        loading.value = false;
    }
};

const resetFilters = () => {
  filters.value = { q_name: '', f_status: [], f_level: [] };
  currentPage.value = 1;
  fetchCompanies(); // بعد از پاک کردن، دوباره لیست را می‌گیرد
};

const viewCompanyProfile = (companyId) => {
  router.push({ name: 'company-profile', params: { id: companyId } });
};

onMounted(fetchCompanies);
</script>

<style scoped>
/* (کدهای CSS عمومی صفحه) */
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
.name-cell { position: relative; cursor: pointer; }
.context-menu { position: absolute; top: 100%; right: 0; background-color: white; border: 1px solid #ddd; border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); z-index: 10; min-width: 150px; visibility: hidden; opacity: 0; transform: translateY(10px); transition: all 0.2s ease-in-out; }
.name-cell:hover .context-menu { visibility: visible; opacity: 1; transform: translateY(0); }
.context-menu button { display: block; width: 100%; padding: 10px 15px; border: none; background: none; text-align: right; cursor: pointer; font-family: 'Vazirmatn', sans-serif; font-size: 0.95em; }
.context-menu button:hover { background-color: #f5f5f5; }
/* ✅ table-footer قدیمی حذف شد و توسط کامپوننت جایگزین شد */
/* .table-footer { ... } */

/* ✅ استایل‌های یکپارچه فیلتر (کپی شده از UsersView) */
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
select.filter-select,
:deep(.multiselect-filter),
:deep(.datepicker-filter input) {
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
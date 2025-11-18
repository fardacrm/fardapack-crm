<template>
    <div class="page-content">
        
        <div class="page-header">
            <h2>📞 لیست تماس‌ها</h2>
            <!-- ✅ تغییر نام به openCallModal برای هماهنگی با منو هاور -->
            <button @click="openCallModal()" class="add-new-button">+ ثبت تماس جدید</button>
        </div>
        
        <!-- ✅ استفاده از کامپوننت استاندارد AppFilter -->
        <AppFilter @filter="fetchCalls" @reset="resetFilters">
            <template #inputs>
                <!-- فیلتر جستجوی متنی -->
                <div class="filter-item">
                    <span class="icon">🔍</span>
                    <input 
                        v-model="filters.name_query" 
                        type="text" 
                        placeholder="جستجوی نام کاربر/شرکت..."
                    />
                </div>
                
                <!-- فیلتر وضعیت‌ها -->
                <div class="filter-item">
                    <span class="icon">📊</span>
                    <Multiselect
                        v-model="filters.statuses"
                        mode="tags"
                        placeholder="انتخاب وضعیت‌ها"
                        :options="CALL_STATUSES"
                        :close-on-select="false"
                        class="multiselect-filter"
                    />
                </div>
                
                <!-- فیلتر تاریخ شروع -->
                <div class="filter-item">
                    <span class="icon">📅</span>
                    <date-picker
                        v-model="filters.start"
                        format="YYYY-MM-DD"
                        display-format="jYYYY/jMM/jDD"
                        placeholder="از تاریخ..."
                        class="datepicker-filter"
                    />
                </div>

                <!-- فیلتر تاریخ پایان -->
                <div class="filter-item">
                    <span class="icon">📅</span>
                    <date-picker
                        v-model="filters.end"
                        format="YYYY-MM-DD"
                        display-format="jYYYY/jMM/jDD"
                        placeholder="تا تاریخ..."
                        class="datepicker-filter"
                    />
                </div>
            </template>
        </AppFilter>

        <div v-if="loading" class="loading-message">در حال بارگذاری اطلاعات تماس‌ها...</div>
        <div v-show="error" class="error-detail">خطا: {{ error }}</div>
        <div v-if="saveSuccess" class="success-message">تماس با موفقیت ثبت شد!</div>
        
        <table v-if="calls.length > 0 && !loading">
            <thead>
                <tr>
                    <th>نام کاربر</th>
                    <th>شرکت</th>
                    <th>تاریخ و زمان</th>
                    <th>وضعیت</th>
                    <th>کارشناس</th>
                </tr>
            </thead>
            <tbody>
                <!-- نمایش ردیف‌های برش‌خورده (Pagination سمت کلاینت) -->
                <tr v-for="call in currentCalls" :key="call.ID">
                    <!-- ✅ سلول نام کاربر با منوی هاور -->
                    <td class="name-cell">
                        <span>{{ call.نام_کاربر }}</span>
                        <div class="context-menu">
                            <!-- فرض بر این است که call.user_id موجود است -->
                            <button @click="viewUserProfile(call.user_id)">👁 نمایش پروفایل</button>
                            <button @click="openUserModal(call.user_id)">✏️ ویرایش کاربر</button>
                            <button @click="openCallModal(call.user_id)">📞 ثبت تماس</button>
                            <button @click="openFollowupModal(call.user_id)">🗓️ ثبت پیگیری</button>
                        </div>
                    </td>
                    <td>{{ call.شرکت }}</td>
                    <td>{{ formatJalaliDateTime(call.تاریخ_و_زمان) }}</td>
                    <td><StatusBadge :text="call.وضعیت" /></td>
                    <td>{{ call.کارشناس_فروش }}</td>
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

        <p v-if="calls.length === 0 && !loading" class="loading-message">
            تماسی یافت نشد.
        </p>
    </div>
    
    <!-- ✅ مدال اصلی تماس‌ها -->
    <CallFormModal
      v-if="showCallModal"
      :preselectedUserId="targetUserId"
      @close="closeCallModal"
      @save="handleCallSave"
    />
    <!-- ✅ مدال ویرایش کاربر (از منوی هاور) -->
    <UserFormModal 
        v-if="showUserModal" 
        :initialData="editingUser"
        @close="closeUserModal" 
        @save="handleUserSave" 
    />
    <!-- ✅ مدال ثبت پیگیری (از منوی هاور) -->
    <FollowupFormModal 
        v-if="showFollowupModal" 
        :preselectedUserId="targetUserId" 
        @close="closeFollowupModal" 
        @save="handleFollowupSave" 
    />
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'; // ✅ اضافه شدن computed
import { useRouter } from 'vue-router'; 
import api from '../api/index.js';
import AppFilter from '../components/AppFilter.vue'; 
import TableFooter from '../components/TableFooter.vue'; // ✅ ایمپورت جدید
import StatusBadge from '../components/StatusBadge.vue';
import CallFormModal from '../components/CallFormModal.vue';
import UserFormModal from '../components/UserFormModal.vue'; 
import FollowupFormModal from '../components/FollowupFormModal.vue'; 
import { formatJalaliDateTime } from '../utils/formatters.js';
import Multiselect from '@vueform/multiselect';
import '@vueform/multiselect/themes/default.css';
import DatePicker from 'vue3-persian-datetime-picker';

const router = useRouter(); 
const CALL_STATUSES = ["ناموفق", "موفق", "خاموش", "رد تماس"];

const calls = ref([]);
const loading = ref(true);
const error = ref(null);
const saveSuccess = ref(false);

const showCallModal = ref(false); 
const showUserModal = ref(false);
const showFollowupModal = ref(false);

const targetUserId = ref(null);
const editingUser = ref(null); 

// ✅ وضعیت‌های Pagination
const totalRecords = ref(0); 
const pageSize = ref(20); 
const currentPage = ref(1); 

const filters = ref({
  name_query: '',
  statuses: [],
  start: '',
  end: ''
});

// --- منطق Pagination در سمت کلاینت ---
const currentCalls = computed(() => {
    if (pageSize.value === 'all') {
        return calls.value;
    }
    const limit = parseInt(pageSize.value);
    const start = (currentPage.value - 1) * limit;
    const end = start + limit;
    return calls.value.slice(start, end);
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


// --- توابع باز کردن/بستن مدال‌ها و ذخیره (بدون تغییر در منطق) ---
const openCallModal = (userId = null) => { 
    targetUserId.value = userId; 
    showCallModal.value = true; 
};
const closeCallModal = () => { 
    showCallModal.value = false;
    targetUserId.value = null;
};
const openUserModal = async (userId) => {
    if (!userId) { error.value = 'شناسه کاربر نامشخص است.'; return; }
    targetUserId.value = userId;
    try {
        const response = await api.get(`/users/${userId}`);
        editingUser.value = response.data;
        showUserModal.value = true;
    } catch (err) {
        error.value = 'خطا در واکشی اطلاعات کاربر برای ویرایش.';
    }
};
const closeUserModal = () => {
    showUserModal.value = false;
    editingUser.value = null;
    targetUserId.value = null;
    fetchCalls(); 
};
const openFollowupModal = (userId) => {
    targetUserId.value = userId;
    showFollowupModal.value = true;
};
const closeFollowupModal = () => {
    showFollowupModal.value = false;
    targetUserId.value = null;
};
const handleCallSave = async (formData) => {
  error.value = null; saveSuccess.value = false;
  try {
    await api.post('/calls', formData);
    saveSuccess.value = true;
    closeCallModal();
    fetchCalls();
    setTimeout(() => { saveSuccess.value = false; }, 3000);
  } catch (err) {
    if (err.response && err.response.data && err.response.data.detail) {
      error.value = err.response.data.detail;
    } else { error.value = 'خطا در ثبت تماس.'; }
    console.error('Error saving call:', err);
  }
};
const handleUserSave = async (formData, userId) => {
    error.value = null; saveSuccess.value = false;
    try {
        if (userId) { await api.put(`/users/${userId}`, formData); } 
        else { await api.post('/users', formData); }
        saveSuccess.value = true; closeUserModal(); 
        setTimeout(() => { saveSuccess.value = false; }, 3000);
    } catch (err) {
        error.value = 'خطا در ذخیره کاربر.';
    }
};
const handleFollowupSave = async (formData) => {
    error.value = null; saveSuccess.value = false;
    try {
        await api.post('/followups', formData);
        saveSuccess.value = true; closeFollowupModal(); 
        setTimeout(() => { saveSuccess.value = false; }, 3000);
    } catch (err) {
        error.value = 'خطا در ثبت پیگیری.';
    }
};


// (تابع واکشی)
const fetchCalls = async () => {
    loading.value = true;
    error.value = null;

    const params = new URLSearchParams();
    if (filters.value.name_query) params.append('name_query', filters.value.name_query);
    if (filters.value.start) params.append('start', filters.value.start);
    if (filters.value.end) params.append('end', filters.value.end);
    
    filters.value.statuses.forEach(status => {
      params.append('statuses', status);
    });

    try {
        const response = await api.get('/calls', { params: params });
        const data = response.data.data || response.data;
        
        calls.value = data.map(call => ({
            ...call,
            user_id: call.ID_کاربر 
        }));
        totalRecords.value = data.length; // ✅ آپدیت totalRecords

        const limit = parseInt(pageSize.value);
        const totalPages = Math.ceil(totalRecords.value / limit);
        if (currentPage.value > totalPages) {
            currentPage.value = totalPages > 0 ? totalPages : 1;
        }

    } catch (err) {
        error.value = err.message || 'خطای ناشناس';
        calls.value = [];
        totalRecords.value = 0;
    } finally {
        loading.value = false;
    }
};

const resetFilters = () => {
  filters.value = { name_query: '', statuses: [], start: '', end: '' };
  currentPage.value = 1;
  fetchCalls(); 
};

const viewUserProfile = (userId) => {
  if (userId) {
    router.push({ name: 'user-profile', params: { id: userId } });
  } else {
    error.value = 'شناسه کاربر نامشخص است.';
  }
};

onMounted(fetchCalls);
</script>

<style scoped>
/* (استایل‌های عمومی صفحه) */
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

/* ✅ استایل‌های منو هاور (Context Menu) - اضافه شده */
.name-cell { position: relative; cursor: pointer; }
.context-menu { position: absolute; top: 100%; right: 0; background-color: white; border: 1px solid #ddd; border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); z-index: 10; min-width: 150px; visibility: hidden; opacity: 0; transform: translateY(10px); transition: all 0.2s ease-in-out; }
.name-cell:hover .context-menu { visibility: visible; opacity: 1; transform: translateY(0); }
.context-menu button { display: block; width: 100%; padding: 10px 15px; border: none; background: none; text-align: right; cursor: pointer; font-family: 'Vazirmatn', sans-serif; font-size: 0.95em; }
.context-menu button:hover { background-color: #f5f5f5; }

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
:deep(.datepicker-filter input) {
  padding-right: 35px; 
  cursor: pointer;
}
:deep(.datepicker-filter) {
  width: 100%;
}
</style>
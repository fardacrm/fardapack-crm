<template>
    <div class="page-content">
        
        <div class="page-header">
            <h2>🗓️ لیست پیگیری‌ها</h2>
            <button @click="openFollowupModal()" class="add-new-button">+ ثبت پیگیری جدید</button>
        </div>
        
        <!-- ✅ استفاده از کامپوننت استاندارد AppFilter -->
        <AppFilter @filter="fetchFollowups" @reset="resetFilters">
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
                        :options="TASK_STATUSES"
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
                        placeholder="از تاریخ پیگیری..."
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
                        placeholder="تا تاریخ پیگیری..."
                        class="datepicker-filter"
                    />
                </div>
            </template>
        </AppFilter>

        <div v-if="loading" class="loading-message">در حال بارگذاری اطلاعات پیگیری‌ها...</div>
        <div v-show="error" class="error-detail">خطا: {{ error }}</div>
        <div v-if="saveSuccess" class="success-message">عملیات با موفقیت انجام شد!</div>
        
        <table v-if="followups.length > 0 && !loading">
            <thead>
                <tr>
                    <!-- ✅ نام کاربر ستون اول شد -->
                    <th>نام کاربر</th>
                    <!-- ✅ عنوان ستون دوم شد -->
                    <th>عنوان</th>
                    <th>شرکت</th>
                    <th>تاریخ پیگیری</th>
                    <th>وضعیت</th>
                    <th>کارشناس</th>
                </tr>
            </thead>
            <tbody>
                <!-- نمایش ردیف‌های برش‌خورده (Pagination سمت کلاینت) -->
                <tr v-for="task in currentFollowups" :key="task.ID">
                    <!-- ✅ سلول نام کاربر با منوی هاور -->
                    <td class="name-cell">
                        <span>{{ task.نام_کاربر }}</span>
                        <div class="context-menu">
                            <!-- فرض بر این است که task.user_id یا task.ID_کاربر موجود است -->
                            <button @click="viewUserProfile(task.user_id)">👁 نمایش پروفایل</button>
                            <!-- ارسال شناسه کاربر برای ویرایش -->
                            <button @click="openUserModal(task.user_id)">✏️ ویرایش کاربر</button>
                            <button @click="openCallModal(task.user_id)">📞 ثبت تماس</button>
                            <button @click="openFollowupModal(task.user_id)">🗓️ ثبت پیگیری</button>
                        </div>
                    </td>
                    <!-- ✅ عنوان ستون دوم -->
                    <td>{{ task.عنوان }}</td>
                    
                    <td>{{ task.شرکت }}</td>
                    <td>{{ formatJalaliDateTime(task.تاریخ_پیگیری) }}</td>
                    <td>
                      <select 
                        v-model="task.وضعیت" 
                        @change="handleStatusChange(task.ID, $event.target.value)"
                        class="status-select"
                        :class="getStatusClass(task.وضعیت)"
                      >
                        <option value="در حال انجام">در حال انجام</option>
                        <option value="پایان یافته">پایان یافته</option>
                      </select>
                    </td>
                    <td>{{ task.کارشناس_فروش }}</td>
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

        <p v-if="followups.length === 0 && !loading" class="loading-message">
            پیگیری یافت نشد.
        </p>
    </div>
    
    <!-- ✅ مدال‌های مورد نیاز از منوی هاور -->
    <!-- مدال اصلی پیگیری (Followup) -->
    <FollowupFormModal
      v-if="showFollowupModal"
      :preselectedUserId="targetUserId"
      @close="closeFollowupModal"
      @save="handleSave"
    />
    <!-- مدال ویرایش کاربر (User) -->
    <UserFormModal 
        v-if="showUserModal" 
        :preselectedUserId="targetUserId" 
        @close="closeUserModal" 
        @save="handleUserSave" 
    />
    <!-- مدال ثبت تماس (Call) -->
    <CallFormModal 
        v-if="showCallModal" 
        :preselectedUserId="targetUserId" 
        @close="closeCallModal" 
        @save="handleCallSave" 
    />
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'; // ✅ اضافه شدن computed
import { useRouter } from 'vue-router'; // ✅ ایمپورت برای مسیریابی پروفایل
import api from '../api/index.js';
import AppFilter from '../components/AppFilter.vue'; 
import TableFooter from '../components/TableFooter.vue'; // ✅ ایمپورت جدید
import FollowupFormModal from '../components/FollowupFormModal.vue';
import UserFormModal from '../components/UserFormModal.vue'; // ✅ ایمپورت
import CallFormModal from '../components/CallFormModal.vue'; // ✅ ایمپورت
import { formatJalaliDateTime } from '../utils/formatters.js';
import Multiselect from '@vueform/multiselect';
import '@vueform/multiselect/themes/default.css';
import DatePicker from 'vue3-persian-datetime-picker';

const router = useRouter(); 
const TASK_STATUSES = ["در حال انجام", "پایان یافته"];

const followups = ref([]);
const loading = ref(true);
const error = ref(null);
const saveSuccess = ref(false);

// ✅ وضعیت‌های Pagination
const totalRecords = ref(0); 
const pageSize = ref(20); 
const currentPage = ref(1); 

// ✅ تغییر نام و اضافه کردن وضعیت‌های جدید برای مدال‌ها
const showFollowupModal = ref(false); 
const showUserModal = ref(false);
const showCallModal = ref(false);
const targetUserId = ref(null);
const editingUser = ref(null); 

const filters = ref({
  name_query: '',
  statuses: [],
  start: '',
  end: ''
});

// --- منطق Pagination در سمت کلاینت ---
const currentFollowups = computed(() => {
    if (pageSize.value === 'all') {
        return followups.value;
    }
    const limit = parseInt(pageSize.value);
    const start = (currentPage.value - 1) * limit;
    const end = start + limit;
    return followups.value.slice(start, end);
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
const openFollowupModal = (userId = null) => { 
    targetUserId.value = userId;
    showFollowupModal.value = true; 
};
const closeFollowupModal = () => { 
    showFollowupModal.value = false;
    targetUserId.value = null;
};
const openUserModal = async (userId) => {
    if (!userId) return;
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
};
const openCallModal = (userId) => {
    targetUserId.value = userId;
    showCallModal.value = true;
};
const closeCallModal = () => {
    showCallModal.value = false;
    targetUserId.value = null;
};
const handleSave = async (formData) => {
  error.value = null; saveSuccess.value = false;
  try {
    await api.post('/followups', formData);
    saveSuccess.value = true;
    closeFollowupModal();
    fetchFollowups();
    setTimeout(() => { saveSuccess.value = false; }, 3000);
  } catch (err) {
    if (err.response && err.response.data && err.response.data.detail) {
      error.value = err.response.data.detail;
    } else { error.value = 'خطا در ثبت پیگیری.'; }
    console.error('Error saving followup:', err);
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
const handleCallSave = async (formData) => {
    error.value = null; saveSuccess.value = false;
    try {
        await api.post('/calls', formData);
        saveSuccess.value = true; closeCallModal(); 
        setTimeout(() => { saveSuccess.value = false; }, 3000);
    } catch (err) {
        error.value = 'خطا در ثبت تماس.';
    }
};


// (تابع واکشی اصلی)
const fetchFollowups = async () => {
    loading.value = true; error.value = null;

    const params = new URLSearchParams();
    if (filters.value.name_query) params.append('name_query', filters.value.name_query);
    if (filters.value.start) params.append('start', filters.value.start);
    if (filters.value.end) params.append('end', filters.value.end);
    
    filters.value.statuses.forEach(status => {
      params.append('statuses', status);
    });

    try {
        const response = await api.get('/followups', { params: params });
        const data = response.data.data || response.data;

        followups.value = data.map(task => ({
            ...task,
            user_id: task.ID_کاربر 
        }));
        totalRecords.value = data.length; // ✅ آپدیت totalRecords
        
        const limit = parseInt(pageSize.value);
        const totalPages = Math.ceil(totalRecords.value / limit);
        if (currentPage.value > totalPages) {
            currentPage.value = totalPages > 0 ? totalPages : 1;
        }

    } catch (err) {
        error.value = err.message || 'خطای ناشناس';
        followups.value = [];
        totalRecords.value = 0;
    } finally {
        loading.value = false;
    }
};

const handleStatusChange = async (taskId, newStatus) => {
  error.value = null; saveSuccess.value = false;
  try {
    await api.put(`/followups/${taskId}/status`, { status: newStatus });
    saveSuccess.value = true;
    setTimeout(() => { saveSuccess.value = false; }, 2000);
  } catch (err) {
    error.value = 'خطا در به‌روزرسانی وضعیت.';
    fetchFollowups(); 
  }
};

const getStatusClass = (status) => {
  if (status === 'پایان یافته') return 'status-green';
  return 'status-orange';
};

const resetFilters = () => {
  filters.value = { name_query: '', statuses: [], start: '', end: '' };
  currentPage.value = 1;
  fetchFollowups(); 
};

const viewUserProfile = (userId) => {
  if (userId) {
    router.push({ name: 'user-profile', params: { id: userId } });
  } else {
    error.value = 'شناسه کاربر نامشخص است.';
  }
};

onMounted(fetchFollowups);
</script>

<style scoped>
/* کدهای عمومی و مدال‌های وضعیت */
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

/* ✅ استایل‌های منو هاور (Context Menu) - کپی شده از UsersView */
.name-cell { position: relative; cursor: pointer; }
.context-menu { position: absolute; top: 100%; right: 0; background-color: white; border: 1px solid #ddd; border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); z-index: 10; min-width: 150px; visibility: hidden; opacity: 0; transform: translateY(10px); transition: all 0.2s ease-in-out; }
.name-cell:hover .context-menu { visibility: visible; opacity: 1; transform: translateY(0); }
.context-menu button { display: block; width: 100%; padding: 10px 15px; border: none; background: none; text-align: right; cursor: pointer; font-family: 'Vazirmatn', sans-serif; font-size: 0.95em; }
.context-menu button:hover { background-color: #f5f5f5; }

/* (CSS دراپ‌داون وضعیت) */
.status-select {
  padding: 5px 8px; border-radius: 15px; border: 1px solid;
  font-family: 'Vazirmatn', sans-serif; font-weight: 600; cursor: pointer;
  -webkit-appearance: none; -moz-appearance: none; appearance: none;
  background-position: left 8px center; background-repeat: no-repeat;
  background-image: url("data:image/svg+xml;utf8,<svg fill='black' height='24' viewBox='0 0 24 24' width='24' xmlns='http://www.w3.org/2000/svg'><path d='M7 10l5 5 5-5z'/><path d='M0 0h24v24H0z' fill='none'/></svg>");
  padding-left: 30px; 
}
.status-green { background-color: #E6F7E6; color: #006400; border-color: #B2D8B2; }
.status-orange { background-color: #FFF3E0; color: #E65100; border-color: #FFD180; }
/* ✅ table-footer قدیمی حذف شد و توسط کامپوننت جایگزین شد */
/* .table-footer { ... } */

/* ✅ استایل‌های یکپارچه فیلتر */
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
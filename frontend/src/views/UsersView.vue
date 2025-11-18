<template>
    <div class="page-content">
        
        <div class="page-header">
            <h2>👥 لیست کاربران و مخاطبین</h2>
            <div>
              <button 
                v-if="currentUser.role === 'admin'"
                @click="openImportModal" 
                class="import-button"
              >
                📥 ایمپورت اکسل
              </button>
              <button @click="openUserModal()" class="add-new-button">+ افزودن کاربر جدید</button>
            </div>
        </div>
        
        <!-- ✅ استفاده از کامپوننت جدید AppFilter -->
        <AppFilter @filter="fetchUsers" @reset="resetFilters">
            <template #inputs>
                <!-- فیلتر نام -->
                <div class="filter-item">
                    <span class="icon">👤</span>
                    <input v-model="filters.first_q" type="text" placeholder="جستجوی نام..."/>
                </div>
                
                <!-- فیلتر نام خانوادگی -->
                <div class="filter-item">
                    <span class="icon">👥</span>
                    <input v-model="filters.last_q" type="text" placeholder="جستجوی نام خانوادگی..."/>
                </div>
                
                <!-- فیلتر تلفن -->
                <div class="filter-item">
                    <span class="icon">📞</span>
                    <input v-model="filters.phone_q" type="text" placeholder="جستجوی تلفن..."/>
                </div>
                
                <!-- فیلتر سمت -->
                <div class="filter-item">
                    <span class="icon">🧑‍💼</span>
                    <input v-model="filters.role_q" type="text" placeholder="جستجوی سمت..."/>
                </div>
                
                <!-- فیلتر حوزه فعالیت -->
                <div class="filter-item">
                    <span class="icon">🔧</span>
                    <input v-model="filters.domain_q" type="text" placeholder="جستجوی حوزه فعالیت..."/>
                </div>
                
                <!-- فیلتر وضعیت‌ها (Multiselect) -->
                <div class="filter-item">
                    <span class="icon">📊</span>
                    <Multiselect
                        v-model="filters.statuses"
                        mode="tags"
                        placeholder="انتخاب وضعیت‌ها"
                        :options="USER_STATUSES"
                        :close-on-select="false"
                        class="multiselect-filter"
                    />
                </div>
                
                <!-- فیلتر سطح‌ها (Multiselect) -->
                <div class="filter-item">
                    <span class="icon">🌟</span>
                    <Multiselect
                        v-model="filters.levels"
                        mode="tags"
                        placeholder="انتخاب سطح‌ها"
                        :options="LEVELS"
                        :close-on-select="false"
                        class="multiselect-filter"
                    />
                </div>
                
                <!-- فیلتر پیگیری باز -->
                <div class="filter-item">
                    <span class="icon">🗓️</span>
                    <select v-model="filters.has_open_task" class="filter-select">
                        <option value="">پیگیری باز؟ (همه)</option>
                        <option value="true">بله</option>
                        <option value="false">خیر</option>
                    </select>
                </div>

                <!-- فیلتر تاریخ از -->
                <div class="filter-item">
                    <span class="icon">📅</span>
                    <date-picker
                        v-model="filters.created_from"
                        format="YYYY-MM-DD"
                        display-format="jYYYY/jMM/jDD"
                        placeholder="تاریخ ایجاد (از)"
                        class="datepicker-filter"
                    />
                </div>

                <!-- فیلتر تاریخ تا -->
                <div class="filter-item">
                    <span class="icon">📅</span>
                    <date-picker
                        v-model="filters.created_to"
                        format="YYYY-MM-DD"
                        display-format="jYYYY/jMM/jDD"
                        placeholder="تاریخ ایجاد (تا)"
                        class="datepicker-filter"
                    />
                </div>
            </template>
        </AppFilter>

        <div v-if="loading" class="loading-message">در حال بارگذاری اطلاعات کاربران...</div>
        <div v-show="error" class="error-detail">خطا: {{ error }}</div>
        <div v-if="saveSuccess" class="success-message">عملیات با موفقیت انجام شد!</div>
        
        <table v-if="users.length > 0 && !loading">
            <thead>
                <tr>
                    <th v-if="currentUser.role === 'admin'" class="checkbox-col"><input type="checkbox" @change="toggleSelectAll" :checked="selectedUsers.length === currentUsers.length"/></th>
                    <th>نام کامل</th>
                    <th>شرکت</th>
                    <th>تلفن</th>
                    <th>وضعیت</th>
                    <th>آخرین تماس</th>
                    <th>پیگیری باز</th>
                    <th>کارشناس</th>
                </tr>
            </thead>
            <tbody>
                <!-- ✅ نمایش ردیف‌های برش‌خورده (فقط برای صفحه فعلی) -->
                <tr v-for="user in currentUsers" :key="user.ID">
                    <td v-if="currentUser.role === 'admin'" class="checkbox-col"><input type="checkbox" v-model="selectedUsers" :value="user.ID"/></td>
                    <!-- منوی هاور نام کاربر (حفظ شده) -->
                    <td class="name-cell">
                        <span>{{ user.نام_کامل }}</span>
                        <div class="context-menu">
                            <button @click="viewUserProfile(user.ID)">👁 نمایش پروفایل</button>
                            <button @click="openUserModal(user)">✏️ ویرایش کاربر</button>
                            <button @click="openCallModal(user.ID)">📞 ثبت تماس</button>
                            <button @click="openFollowupModal(user.ID)">🗓️ ثبت پیگیری</button>
                        </div>
                    </td>
                    <!-- ✅ ستون شرکت (حالت ساده) -->
                    <td>
                        <span>{{ user.شرکت }}</span>
                    </td>
                    <td>{{ user.تلفن }}</td>
                    <td><StatusBadge :text="user.وضعیت_کاربر" /></td>
                    <td>
                        <StatusBadge 
                            :text="formatJalaliDateTime(user.آخرین_تماس) || 'ندارد'" 
                            :callStatus="user.آخرین_وضعیت_تماس" 
                        />
                    </td>
                    <td><StatusBadge :text="formatJalaliDate(user.وضعیت_پیگیری_باز)" /></td>
                    <td>{{ user.کارشناس_فروش }}</td>
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

        <p v-if="users.length === 0 && !loading" class="loading-message">
            داده مطابق با فیلتر شما وجود ندارد.
        </p>
        
        <div v-if="selectedUsers.length > 0 && currentUser.role === 'admin'" class="bulk-action-bar">
            <span>{{ selectedUsers.length }} کاربر انتخاب شده</span>
            <div class="bulk-actions">
                <select v-model="bulkAssignOwnerId">
                    <option :value="null">-- انتخاب کارشناس جدید --</option>
                    <option v-for="agent in salesAgents" :key="agent.id" :value="agent.id">
                        {{ agent.username }} ({{ agent.role === 'admin' ? 'مدیر' : 'کارشناس' }})
                    </option>
                </select>
                <button @click="handleBulkAssign" class="btn-apply-bulk">اعمال تغییر کارشناس</button>
            </div>
        </div>
    </div>
    
    <UserFormModal v-if="showUserModal" :initialData="editingUser" @close="closeUserModal" @save="handleUserSave" />
    <CallFormModal v-if="showCallModal" :preselectedUserId="targetUserId" @close="closeCallModal" @save="handleCallSave" />
    <FollowupFormModal v-if="showFollowupModal" :preselectedUserId="targetUserId" @close="closeFollowupModal" @save="handleFollowupSave" />
    <ImportExcelModal v-if="showImportModal" @close="closeImportModal" @import-success="handleImportSuccess" />
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'; // ✅ ایمپورت computed
import { useRouter } from 'vue-router';
import AppFilter from '../components/AppFilter.vue';
import UserFormModal from '../components/UserFormModal.vue';
import CallFormModal from '../components/CallFormModal.vue';
import FollowupFormModal from '../components/FollowupFormModal.vue';
import ImportExcelModal from '../components/ImportExcelModal.vue';
import TableFooter from '../components/TableFooter.vue'; // ✅ ایمپورت جدید
import api from '../api/index.js'; 
import StatusBadge from '../components/StatusBadge.vue';
import Multiselect from '@vueform/multiselect';
import '@vueform/multiselect/themes/default.css';
import { formatJalaliDate, formatJalaliDateTime, toEnglishDigits } from '../utils/formatters.js';
import DatePicker from 'vue3-persian-datetime-picker';

const router = useRouter();
const USER_STATUSES = [ 'بدون وضعیت', 'در حال پیگیری', 'پیش فاکتور', 'مشتری شد', 'لغو' ];
const LEVELS = ["هیچکدام", "طلایی", "نقره‌ای", "برنز"]; 

const users = ref([]);
const loading = ref(true);
const error = ref(null);
const saveSuccess = ref(false);
const selectedUsers = ref([]); 
const salesAgents = ref([]); 
const bulkAssignOwnerId = ref(null); 
const currentUser = ref({ role: 'guest' }); 

const showUserModal = ref(false); 
const editingUser = ref(null); 
const showCallModal = ref(false);
const showFollowupModal = ref(false);
const targetUserId = ref(null);
const showImportModal = ref(false);

// ✅ وضعیت‌های Pagination
const totalRecords = ref(0); 
const pageSize = ref(20); // ✅ پیش‌فرض 20
const currentPage = ref(1); // ✅ صفحه فعلی

// آبجکت فیلترها (بدون تغییر)
const filters = ref({
  first_q: '',
  last_q: '',
  phone_q: '',
  role_q: '',
  domain_q: '',
  statuses: [], 
  levels: [],
  has_open_task: '',
  created_from: '',
  created_to: ''
});

// --- منطق نمایش Pagination در سمت کلاینت ---

// ✅ نمایش کاربران صفحه فعلی
const currentUsers = computed(() => {
    if (pageSize.value === 'all') {
        return users.value;
    }
    const limit = parseInt(pageSize.value);
    const start = (currentPage.value - 1) * limit;
    const end = start + limit;
    
    // در این منطق فرض شده که API کل دیتا را برمی‌گرداند.
    // اگر API از Pagination سمت سرور پشتیبانی می‌کرد، فقط نیاز به استفاده از users.value بود.
    return users.value.slice(start, end);
});

// ✅ توابع Pagination
const updatePageSize = (newSize) => {
    pageSize.value = newSize === 'all' ? 'all' : parseInt(newSize);
    currentPage.value = 1; // ریست به صفحه اول
    fetchUsers();
};

const goToPage = (page) => {
    // محدود کردن ناوبری
    const limit = parseInt(pageSize.value);
    const totalPages = Math.ceil(totalRecords.value / limit);
    
    if (page >= 1 && page <= totalPages) {
        currentPage.value = page;
        // 💡 چون فرض بر این است که API کل داده‌ها را می‌دهد، فقط UI را به‌روز می‌کنیم.
    }
};
// --- پایان منطق Pagination ---


// (منطق مدال‌ها و ذخیره‌سازی بدون تغییر)
const openUserModal = (user = null) => {
  if (user) { editingUser.value = user; } else { editingUser.value = null; }
  showUserModal.value = true;
};
const closeUserModal = () => {
  showUserModal.value = false;
  editingUser.value = null;
};
const openCallModal = (userId) => {
  targetUserId.value = userId;
  showCallModal.value = true;
};
const closeCallModal = () => {
  showCallModal.value = false;
  targetUserId.value = null;
};
const openFollowupModal = (userId) => {
  targetUserId.value = userId;
  showFollowupModal.value = true;
};
const closeFollowupModal = () => {
  showFollowupModal.value = false;
  targetUserId.value = null;
};
const openImportModal = () => {
  showImportModal.value = true;
};
const closeImportModal = () => {
  showImportModal.value = false;
};
const handleImportSuccess = () => {
  fetchUsers(); 
};
const handleUserSave = async (formData, userId) => {
  error.value = null; saveSuccess.value = false;
  const dataToSend = { ...formData };
  if (dataToSend.company_id === "" || dataToSend.company_id === 0) { dataToSend.company_id = null; }
  if (dataToSend.company_id !== null && dataToSend.company_id) { dataToSend.company_id = parseInt(dataToSend.company_id, 10); }
  try {
    if (userId) { await api.put(`/users/${userId}`, dataToSend); } 
    else { await api.post('/users', dataToSend); }
    saveSuccess.value = true; closeUserModal(); fetchUsers();
    setTimeout(() => { saveSuccess.value = false; }, 3000);
  } catch (err) {
    if (err.response && err.response.data && err.response.data.detail) {
      error.value = Array.isArray(err.response.data.detail) ? err.response.data.detail[0].msg : err.response.data.detail;
    } else { error.value = 'خطا در ذخیره کاربر.'; }
  }
};
const handleCallSave = async (formData) => {
  error.value = null; saveSuccess.value = false;
  try {
    await api.post('/calls', formData);
    saveSuccess.value = true; closeCallModal(); fetchUsers();
    setTimeout(() => { saveSuccess.value = false; }, 3000);
  } catch (err) {
    if (err.response && err.response.data && err.response.data.detail) {
      error.value = err.response.data.detail;
    } else { error.value = 'خطا در ثبت تماس.'; }
  }
};
const handleFollowupSave = async (formData) => {
  error.value = null; saveSuccess.value = false;
  try {
    await api.post('/followups', formData);
    saveSuccess.value = true; closeFollowupModal(); fetchUsers(); 
    setTimeout(() => { saveSuccess.value = false; }, 3000);
  } catch (err) {
    if (err.response && err.response.data && err.response.data.detail) {
      error.value = err.response.data.detail;
    } else { error.value = 'خطا در ثبت پیگیری.'; }
  }
};


// تابع واکشی (با تغییرات Pagination)
const fetchUsers = async () => {
    loading.value = true; error.value = null;
    
    const params = new URLSearchParams();
    if (filters.value.first_q) params.append('first_q', filters.value.first_q);
    if (filters.value.last_q) params.append('last_q', filters.value.last_q);
    if (filters.value.phone_q) params.append('phone_q', toEnglishDigits(filters.value.phone_q));
    if (filters.value.role_q) params.append('role_q', filters.value.role_q);
    if (filters.value.domain_q) params.append('domain_q', filters.value.domain_q);
    if (filters.value.created_from) params.append('created_from', toEnglishDigits(filters.value.created_from));
    if (filters.value.created_to) params.append('created_to', toEnglishDigits(filters.value.created_to));
    if (filters.value.has_open_task !== '') params.append('has_open_task', filters.value.has_open_task === 'true');
    
    filters.value.statuses.forEach(status => {
      params.append('statuses', status);
    });
    filters.value.levels.forEach(level => {
      params.append('levels', level);
    });

    try {
        const response = await api.get('/users', { params: params });
        
        // ✅ ما فرض می‌کنیم API همه کاربران را برمی‌گرداند و ما در اینجا Pagination را انجام می‌دهیم
        const data = response.data.data || response.data; 

        users.value = data;
        totalRecords.value = data.length; // ✅ آپدیت totalRecords

        // ✅ اطمینان از ماندن در صفحه صحیح پس از فیلتر
        const limit = parseInt(pageSize.value);
        const totalPages = Math.ceil(totalRecords.value / limit);
        if (currentPage.value > totalPages) {
            currentPage.value = totalPages > 0 ? totalPages : 1;
        }


        selectedUsers.value = [];
    } catch (err) {
        error.value = err.response?.data?.detail || err.message || 'خطای ناشناس';
        users.value = [];
        totalRecords.value = 0;
    } finally {
        loading.value = false;
    }
};

const resetFilters = () => {
  filters.value = {
    first_q: '', last_q: '', phone_q: '', role_q: '', domain_q: '',
    statuses: [], levels: [], has_open_task: '',
    created_from: '', created_to: ''
  };
  currentPage.value = 1; // ریست به صفحه اول
  fetchUsers(); 
};

const toggleSelectAll = (event) => {
  // ✅ انتخاب فقط کاربران صفحه فعلی
  const usersToSelect = event.target.checked ? currentUsers.value.map(user => user.ID) : [];
  
  // حفظ آیتم‌های انتخاب شده از صفحات دیگر (اگر از قبل بودند)
  const usersOnOtherPages = selectedUsers.value.filter(id => !currentUsers.value.map(u => u.ID).includes(id));
  selectedUsers.value = [...usersOnOtherPages, ...usersToSelect];
};

const fetchSalesAgents = async () => {
  try {
    const response = await api.get('/admin/app-users'); 
    salesAgents.value = response.data;
  } catch (err) {
    console.error("خطا در دریافت لیست کارشناسان:", err);
  }
};
const handleBulkAssign = async () => {
  if (bulkAssignOwnerId.value === null) {
    error.value = "لطفاً یک کارشناس جدید را انتخاب کنید."; return;
  }
  if (selectedUsers.value.length === 0) {
    error.value = "هیچ کاربری انتخاب نشده است."; return;
  }
  error.value = null;
  try {
    await api.put('/users/bulk-owner', {
      user_ids: selectedUsers.value,
      new_owner_id: bulkAssignOwnerId.value
    });
    saveSuccess.value = true; fetchUsers(); 
    selectedUsers.value = []; bulkAssignOwnerId.value = null; 
    setTimeout(() => { saveSuccess.value = false; }, 3000);
  } catch (err) {
    error.value = err.response?.data?.detail || 'خطا در اعمال تغییر گروهی.';
  }
};
const fetchCurrentUser = async () => {
  try {
    const response = await api.get('/me');
    currentUser.value = response.data;
  } catch (err) {
    console.error("خطا در دریافت اطلاعات کاربر:", err);
  }
};

const viewUserProfile = (userId) => {
  router.push({ name: 'user-profile', params: { id: userId } });
};

onMounted(async () => {
  await Promise.all([
    fetchCurrentUser(),
    fetchUsers(),
    fetchSalesAgents()
  ]);
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
.page-header div { display: flex; gap: 10px; }
.add-new-button { background-color: #28a745; color: white; border: none; border-radius: 5px; padding: 10px 15px; font-family: 'Vazirmatn', sans-serif; font-size: 1rem; font-weight: 600; cursor: pointer; }
.success-message { color: green; background-color: #e6f7e6; padding: 15px; border-radius: 5px; margin-top: 15px; }

/* ✅ استایل‌های منو هاور نام کاربر (حفظ شد) */
.name-cell { position: relative; cursor: pointer; }
.context-menu { position: absolute; top: 100%; right: 0; background-color: white; border: 1px solid #ddd; border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); z-index: 10; min-width: 150px; visibility: hidden; opacity: 0; transform: translateY(10px); transition: all 0.2s ease-in-out; }
.name-cell:hover .context-menu { visibility: visible; opacity: 1; transform: translateY(0); }

/* ✅ حذف استایل‌های company-cell */
/* .company-cell { position: relative; cursor: pointer; } */
/* .company-cell:hover .context-menu { visibility: visible; opacity: 1; transform: translateY(0); } */

.context-menu button { display: block; width: 100%; padding: 10px 15px; border: none; background: none; text-align: right; cursor: pointer; font-family: 'Vazirmatn', sans-serif; font-size: 0.95em; }
.context-menu button:hover { background-color: #f5f5f5; }

/* ✅ استایل‌های یکپارچه فیلتر (بدون تغییر) */
.filter-item {
  position: relative; 
  flex: 1;
  min-width: 200px;
}
.filter-item .icon {
  position: absolute; right: 12px; top: 50%; transform: translateY(-50%);
  color: #888; z-index: 1;
}
input[type="text"], select.filter-select, :deep(.multiselect-filter), :deep(.datepicker-filter input) {
  width: 100%; box-sizing: border-box; padding: 10px 35px 10px 10px;
  border: 1px solid #ccc; border-radius: 5px; font-family: 'Vazirmatn', sans-serif;
  color: #333; height: 44px;
}
:deep(.multiselect-filter) {
  --ms-padding-left: 10px; --ms-padding-right: 35px; --ms-min-height: 44px; 
  --ms-font-family: 'Vazirmatn', sans-serif; --ms-border-color: #ccc;
  --ms-radius: 5px; --ms-tag-bg: #007bff; --ms-tag-color: white;
}
:deep(.datepicker-filter input) { padding-right: 35px; cursor: pointer; }
:deep(.datepicker-filter) { width: 100%; }

/* (CSS عملیات گروهی بدون تغییر) */
.checkbox-col { width: 40px; text-align: center; }
.bulk-action-bar {
  position: sticky; bottom: 0; left: 0; width: 100%;
  padding: 15px 20px; background-color: #2c3e50;
  color: white; border-top: 2px solid #3498db;
  box-shadow: 0 -2px 10px rgba(0,0,0,0.2);
  display: flex; justify-content: space-between; align-items: center;
  z-index: 500; box-sizing: border-box;
  max-width: 1400px;
  margin: 0 auto;
  border-radius: 0 0 10px 10px;
}
.bulk-actions { display: flex; gap: 10px; }
.bulk-action-bar select {
  padding: 8px; border-radius: 5px; border: 1px solid #ccc;
  font-family: 'Vazirmatn', sans-serif;
}
.btn-apply-bulk {
  background-color: #3498db; color: white; border: none;
  padding: 8px 15px; border-radius: 5px; cursor: pointer;
  font-family: 'Vazirmatn', sans-serif; font-weight: 600;
}
.import-button {
  background-color: #17a2b8; color: white; border: none;
  border-radius: 5px; padding: 10px 15px; font-family: 'Vazirmatn', sans-serif;
  font-size: 1rem; font-weight: 600; cursor: pointer;
}
/* ✅ table-footer قدیمی حذف شد */
/* .table-footer { ... } */
</style>
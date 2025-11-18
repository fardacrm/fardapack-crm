<template>
  <div class="table-pagination-footer">
    
    <!-- بخش انتخاب تعداد ردیف در صفحه -->
    <div class="page-size-selector">
      <span>تعداد ردیف در صفحه:</span>
      <select :value="pageSize" @change="$emit('update:pageSize', $event.target.value)" class="page-size-select">
        <option v-for="size in availableSizes" :key="size" :value="size">
          {{ size === 'all' ? 'همه' : size }}
        </option>
      </select>
    </div>

    <!-- بخش Pagination Controls (دکمه‌های صفحه) -->
    <div class="pagination-controls" v-if="pageSize !== 'all' && totalRecords > 0">
        <button 
            @click="$emit('goToPage', currentPage - 1)" 
            :disabled="currentPage === 1" 
            class="page-nav-btn page-nav-prev"
        >
            <span class="icon-nav">⟨</span> قبلی
        </button>
        
        <span class="page-info">صفحه <span class="current-page-num">{{ currentPage }}</span> از <span class="total-page-num">{{ totalPages }}</span></span>
        
        <button 
            @click="$emit('goToPage', currentPage + 1)" 
            :disabled="currentPage >= totalPages" 
            class="page-nav-btn page-nav-next"
        >
            بعدی <span class="icon-nav">⟩</span>
        </button>
    </div>

    <!-- بخش نمایش اطلاعات کلی -->
    <div class="total-info">
      تعداد کل رکوردها: <span class="total-count">{{ totalRecords.toLocaleString('fa-IR') }}</span>
    </div>

  </div>
</template>

<script setup>
import { computed } from 'vue'; // ✅ ایمپورت اضافه شد

const props = defineProps({
  // تعداد کل رکوردها (از API گرفته می‌شود)
  totalRecords: {
    type: Number,
    required: true,
  },
  // تعداد آیتم‌های قابل نمایش در حال حاضر
  pageSize: {
    type: [Number, String], // می‌تواند عدد یا 'all' باشد
    default: 20,
  },
  // صفحه فعلی (جدید)
  currentPage: {
    type: Number,
    default: 1,
  },
  // گزینه‌های موجود برای انتخاب
  availableSizes: {
    type: Array,
    default: () => [20, 50, 100, 'all'],
  },
});

defineEmits(['update:pageSize', 'goToPage']);

// محاسبه تعداد کل صفحات
const totalPages = computed(() => {
    if (props.pageSize === 'all' || props.pageSize === '0') return 1;
    const size = parseInt(props.pageSize);
    if (size === 0 || props.totalRecords === 0) return 1;
    return Math.ceil(props.totalRecords / size);
});
</script>

<style scoped>
.table-pagination-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background-color: #f0f4f7;
  border-top: 1px solid #e0e0e0;
  border-radius: 0 0 10px 10px;
  margin-top: -1px;
  box-shadow: 0 -2px 5px rgba(0, 0, 0, 0.03);
  font-family: 'Vazirmatn', sans-serif;
  color: #4a5568;
}

.page-size-selector, .total-info, .pagination-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-size-select {
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  background-color: white;
  cursor: pointer;
  font-size: 0.9rem;
  font-family: 'Vazirmatn', sans-serif;
  min-width: 80px;
}

.total-info {
  font-weight: 500;
  color: #333;
}

.total-count {
  font-weight: 700;
  color: #2b6cb0;
  margin-right: 5px;
}

/* استایل‌های Pagination Controls */
.pagination-controls {
    gap: 5px;
    background-color: white;
    padding: 5px;
    border-radius: 8px;
    border: 1px solid #e0e0e0;
}
.page-nav-btn {
    padding: 8px 12px;
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 600;
    transition: background-color 0.2s;
    font-family: 'Vazirmatn', sans-serif;
    display: inline-flex;
    align-items: center;
    gap: 5px;
}
.page-nav-btn:hover:not(:disabled) {
    background-color: #2980b9;
}
.page-nav-btn:disabled {
    background-color: #bdc3c7;
    cursor: not-allowed;
}
.page-info {
    padding: 0 10px;
    font-size: 0.95rem;
    font-weight: 500;
}
.current-page-num, .total-page-num {
    font-weight: 700;
}
.icon-nav {
    font-size: 1.2em;
    line-height: 1;
}

/* استایل‌های ریسپانسیو */
@media (max-width: 768px) {
  .table-pagination-footer {
    flex-direction: column;
    gap: 15px;
    padding: 15px;
  }
  .page-size-selector, .total-info, .pagination-controls {
    width: 100%;
    justify-content: space-between;
  }
  .page-nav-btn {
      flex-grow: 1;
      justify-content: center;
  }
}
</style>
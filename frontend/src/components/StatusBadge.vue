<template>
  <span class="status-badge" :class="colorClass" :title="text">
    {{ formattedText }}
  </span>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  text: {
    type: String,
    default: '—'
  },
  // 💡 [جدید] یک پراپ جدید برای وضعیت تماس (که دیده نمی‌شود اما روی رنگ اثر می‌گذارد)
  callStatus: {
    type: String,
    default: null
  }
});

// 💡 [جدید] تابعی برای فرمت کردن متن (فقط تاریخ را نشان بده، نه ساعت)
const formattedText = computed(() => {
  const status = props.text || '—';
  if (status.includes('/') && status.includes('(')) {
    // فرمت شمسی (۱۴۰۴/۰۸/۲۷ (شنبه))
    return status.split(' ')[0]; // فقط بخش تاریخ
  }
  return status;
});

const colorClass = computed(() => {
  const status = props.text || '—';
  const callStat = props.callStatus;

  // --- منطق رنگ برای وضعیت تماس ---
  if (callStat) {
    if (callStat === 'موفق') return 'status-green';
    if (callStat === 'ناموفق' || callStat === 'رد تماس' || callStat === 'خاموش') return 'status-red';
  }
  // ---

  // --- منطق رنگ برای وضعیت‌های دیگر ---
  if (['مشتری شد', 'تایید شده', 'پایان یافته', 'دارد'].includes(status)) {
    return 'status-green';
  }
  if (['در حال پیگیری'].includes(status)) {
    return 'status-orange';
  }
  if (['لغو', 'رد شده'].includes(status)) {
    return 'status-red';
  }
  if (['پیش فاکتور'].includes(status)) {
    return 'status-blue';
  }
  
  // اگر تاریخ پیگیری باز بود (و کلمه "ندارد" نبود)
  if (status.includes('/') && status !== 'ندارد') {
    return 'status-green';
  }
  
  return 'status-gray'; // پیش‌فرض (شامل "ندارد", "بدون وضعیت" و ...)
});
</script>

<style scoped>
.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 15px;
  font-size: 0.9em;
  font-weight: 600;
  border: 1px solid;
  white-space: nowrap; 
  
  /* 💡 [جدید] برای تاریخ‌های طولانی که کوتاه می‌شوند */
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  vertical-align: middle; /* تراز بهتر در سلول جدول */
}

/* (کلاس‌های رنگی بدون تغییر) */
.status-green { background-color: #E6F7E6; color: #006400; border-color: #B2D8B2; }
.status-orange { background-color: #FFF3E0; color: #E65100; border-color: #FFD180; }
.status-red { background-color: #FFEBEE; color: #C62828; border-color: #FFCDD2; }
.status-blue { background-color: #E3F2FD; color: #0D47A1; border-color: #BBDEFB; }
.status-gray { background-color: #F5F5F5; color: #333333; border-color: #E0E0E0; }
</style>
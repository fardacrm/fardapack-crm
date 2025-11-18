<template>
  <div class="app-filter-container">
    <!-- محل قرارگیری اینپوت‌ها که از کامپوننت والد (مثل UsersView) پاس داده می‌شوند -->
    <slot name="inputs"></slot>

    <!-- بخش دکمه‌های عملیاتی -->
    <div class="filter-actions">
      <button @click="$emit('filter')" class="btn-search">
        <span class="icon-btn">🔍</span>
        جستجو
      </button>
      <button @click="$emit('reset')" class="btn-reset">
        <span class="icon-btn">❌</span>
        پاک کردن
      </button>
      <!-- اسلات اضافی برای دکمه‌های خاص اگر نیاز شد -->
      <slot name="actions"></slot>
    </div>
  </div>
</template>

<script setup>
defineEmits(['filter', 'reset']);
</script>

<style scoped>
.app-filter-container {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  margin-bottom: 20px;
  border: 1px solid #eee;
  align-items: flex-end; /* تراز عمودی عناصر در پایین (هم‌راستا با دکمه‌ها) */
}

.filter-actions {
  display: flex;
  gap: 10px;
  /* دکمه‌ها فضای باقی‌مانده را پر نکنند اما حداقل عرض داشته باشند */
  flex-grow: 0; 
  margin-left: auto; /* هل دادن دکمه‌ها به سمت چپ (در حالت RTL) */
}

.btn-search, .btn-reset {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 0 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-family: 'Vazirmatn', sans-serif; /* فونت فارسی */
  font-weight: 600;
  height: 44px; /* ارتفاع ثابت برای هماهنگی با اینپوت‌ها */
  transition: all 0.2s ease;
  font-size: 0.95rem;
}

.btn-search {
  background-color: #3498db;
  color: white;
  box-shadow: 0 2px 5px rgba(52, 152, 219, 0.3);
}

.btn-search:hover {
  background-color: #2980b9;
  transform: translateY(-1px);
}

.btn-reset {
  background-color: #e0e0e0;
  color: #555;
}

.btn-reset:hover {
  background-color: #d0d0d0;
  color: #333;
}

.icon-btn {
  font-size: 1.1em;
}

/* تنظیمات ریسپانسیو */
@media (max-width: 768px) {
  .app-filter-container {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .filter-actions {
    margin-left: 0;
    width: 100%;
    margin-top: 10px;
  }

  .btn-search, .btn-reset {
    flex: 1; /* دکمه‌ها در موبایل تمام عرض را بگیرند */
  }
}
</style>
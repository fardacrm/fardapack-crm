<template>
    <div class="page-content">
        
        <div class="page-header">
            <h2>📦 مدیریت محصولات</h2>
            <button @click="openModal()" class="add-new-button">+ افزودن محصول جدید</button>
        </div>
        
        <button @click="fetchProducts" class="refresh-button">🔄 بروزرسانی داده‌ها</button>

        <div v-if="loading" class="loading-message">در حال بارگذاری اطلاعات محصولات...</div>
        <div v-show="error" class="error-detail">خطا: {{ error }}</div>
        <div v-if="saveSuccess" class="success-message">عملیات با موفقیت انجام شد!</div>
        
        <table v-if="products.length > 0 && !loading">
            <thead>
                <tr>
                    <th>دسته‌بندی</th>
                    <th>نام محصول</th>
                    <th>عملیات</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="product in products" :key="product.id">
                    <td>{{ product.category }}</td>
                    <td>{{ product.name }}</td>
                    <td>
                      <button @click="openModal(product)" class="btn-edit">✏️ ویرایش</button>
                    </td>
                </tr>
            </tbody>
        </table>
        
        <p v-if="products.length === 0 && !loading" class="loading-message">
            محصولی یافت نشد.
        </p>
    </div>
    
    <ProductFormModal
      v-if="showModal"
      :initialData="editingProduct"
      @close="closeModal"
      @save="handleSave"
    />
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../api/index.js';
import ProductFormModal from '../components/ProductFormModal.vue'; // 👈 مودال محصول

const products = ref([]);
const loading = ref(true);
const error = ref(null);
const saveSuccess = ref(false);
const showModal = ref(false);
const editingProduct = ref(null);

// --- منطق مودال ---
const openModal = (product = null) => {
  editingProduct.value = product;
  showModal.value = true;
};
const closeModal = () => {
  showModal.value = false;
  editingProduct.value = null;
};

// --- تابع ذخیره محصول ---
const handleSave = async (formData, productId) => {
  error.value = null;
  saveSuccess.value = false;
  
  try {
    if (productId) {
      // حالت ویرایش
      await api.put(`/products/${productId}`, formData);
    } else {
      // حالت ایجاد
      await api.post('/products', formData);
    }
    saveSuccess.value = true;
    closeModal();
    fetchProducts(); // رفرش لیست
    setTimeout(() => { saveSuccess.value = false; }, 3000);
  } catch (err) {
    if (err.response && err.response.data && err.response.data.detail) {
      error.value = err.response.data.detail;
    } else {
      error.value = 'خطا در ذخیره محصول.';
    }
    console.error('Error saving product:', err);
  }
};


// تابع واکشی محصولات
const fetchProducts = async () => {
    loading.value = true;
    error.value = null;
    try {
        const response = await api.get('/products');
        products.value = response.data;
    } catch (err) {
        error.value = err.message || 'خطای ناشناس';
        console.error('Error fetching products:', err);
    } finally {
        loading.value = false;
    }
};

onMounted(fetchProducts);
</script>

<style scoped>
/* (کدهای CSS مشابه صفحات قبلی) */
.page-content { padding: 20px; }
.refresh-button { margin-bottom: 20px; padding: 10px 15px; background-color: #3498db; color: white; border: none; border-radius: 5px; cursor: pointer; }
table { width: 100%; border-collapse: collapse; margin-top: 20px; background-color: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
th, td { border: 1px solid #ddd; padding: 12px 15px; text-align: right; vertical-align: middle; }
th { background-color: #f2f2f2; font-weight: 700; color: #333; }
.loading-message { text-align: center; padding: 20px; color: #555; }
.error-detail { color: red; background-color: #ffe0e0; padding: 15px; border-radius: 5px; margin-top: 15px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.add-new-button { background-color: #28a745; color: white; border: none; border-radius: 5px; padding: 10px 15px; font-family: 'Vazirmatn', sans-serif; font-size: 1rem; font-weight: 600; cursor: pointer; }
.success-message { color: green; background-color: #e6f7e6; padding: 15px; border-radius: 5px; margin-top: 15px; }
.btn-edit {
  background-color: #ffc107; /* زرد */
  color: #333;
  border: none;
  padding: 5px 10px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.9em;
}
</style>
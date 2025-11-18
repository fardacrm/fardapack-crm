<template>
  <div class="app-layout">
    <aside class="sidebar">
      <div class="logo">FardaPack CRM</div>
      <nav>
        <router-link to="/dashboard" active-class="active">داشبورد 🏠</router-link>
        <router-link to="/users" active-class="active">کاربران 👥</router-link>
        <router-link to="/companies" active-class="active">شرکت‌ها 🏢</router-link>
        <router-link to="/calls" active-class="active">تماس‌ها 📞</router-link>
        <router-link to="/followups" active-class="active">پیگیری‌ها 🗓️</router-link>
        <router-link to="/orders" active-class="active">سفارشات 🛒</router-link>
        <router-link to="/products" active-class="active">محصولات 📦</router-link>
        
        <router-link 
          v-if="currentUser.role === 'admin'" 
          to="/admin" 
          active-class="active"
        >
          مدیریت دسترسی 🔒
        </router-link>

        <a @click="logout" class="logout-link">خروج 👋</a>
      </nav>
    </aside>

    <main class="main-content">
      <header class="header">
        <span class="user-info">کاربر: {{ currentUser.username }} ({{ currentUser.role === 'admin' ? 'مدیر' : 'کارشناس' }})</span>
      </header>
      
      <div class="page-container">
        <section class="content-wrapper">
          <router-view />
        </section>
      </div>
      
    </main>
  </div>
</template>

<script setup>
// (بخش اسکریپت بدون تغییر است)
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../api/index.js'; 

const router = useRouter();
const currentUser = ref({ username: 'در حال بارگذاری...', role: 'guest' }); 

const fetchCurrentUser = async () => {
    try {
      const response = await api.get('/me');
      currentUser.value = response.data;
    } catch (error) {
      console.error('Error fetching current user:', error);
    }
};

const logout = () => {
    localStorage.removeItem('crm-token');
    router.push('/');
};

onMounted(fetchCurrentUser); 
</script>

<style scoped>
/* (استایل‌های سایدبار و هدر بدون تغییر) */
.app-layout {
  display: flex;
  height: 100vh;
  font-family: 'Vazirmatn', sans-serif;
  background-color: #f4f7f6; /* 💡 [جدید] پس‌زمینه خاکستری سراسری */
}
.sidebar {
  width: 250px;
  background-color: #2c3e50;
  color: #ecf0f1;
  padding: 15px;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  flex-shrink: 0; /* 💡 [جدید] جلوگیری از کوچک شدن سایدبار */
}
.logo {
  font-size: 1.5rem;
  font-weight: 700;
  text-align: center;
  margin-bottom: 25px;
  color: #3498db;
}
nav a, .logout-link {
  display: block;
  color: #ecf0f1;
  text-decoration: none;
  padding: 12px 10px;
  margin-bottom: 5px;
  border-radius: 6px;
  transition: background-color 0.2s;
  cursor: pointer;
}
nav a:hover, .logout-link:hover {
  background-color: #34495e;
}
nav a.active {
  background-color: #3498db;
  font-weight: 600;
}
.main-content {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto; /* 💡 [تغییر] اسکرول به محتوای اصلی منتقل شد */
}
.header {
  background-color: white;
  padding: 15px 30px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  text-align: left;
  font-weight: 600;
  color: #333;
  position: sticky; /* 💡 [جدید] هدر در بالا می‌چسبد */
  top: 0;
  z-index: 100;
}

/* 💡💡💡 [اصلاح نهایی برای حالت جعبه‌ای] 💡💡💡 */
.page-container {
  padding: 20px; /* ایجاد فاصله از اطراف */
  flex-grow: 1;
}
.content-wrapper {
  background-color: #ffffff; /* پس‌زمینه سفید */
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #e0e0e0;
  
  /* ایجاد حالت جعبه‌ای */
  max-width: 1400px; 
  margin: 0 auto; /* وسط‌چین کردن */
  
  /* نکته: فایل‌های View (مثل UsersView.vue) 
    باید padding: 20px خود را حفظ کنند 
    تا محتوا به لبه‌های این کادر سفید نچسبد.
  */
}
</style>
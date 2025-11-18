<template>
  <div class="login-container">
    <div class="login-box">
      <h2>📇 ورود به FardaPack CRM</h2>
      <form @submit.prevent="handleLogin">
        <div class="input-group">
          <label for="username">نام کاربری</label>
          <input
            id="username"
            type="text"
            v-model="username"
            placeholder="admin"
            required
          />
        </div>
        <div class="input-group">
          <label for="password">رمز عبور</label>
          <input
            id="password"
            type="password"
            v-model="password"
            placeholder="admin123"
            required
          />
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <button type="submit" class="login-button" :disabled="loading">
          {{ loading ? 'در حال ورود...' : 'ورود' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

// آدرس بک‌اند شما (که در ترمینال دیگر در حال اجراست)
const API_URL = 'http://127.0.0.1:8000/api';

const username = ref('admin'); // پیش‌فرض برای تست
const password = ref('admin123'); // پیش‌فرض برای تست
const error = ref(null);
const loading = ref(false);
const router = useRouter(); // برای جابجایی بین صفحات

const handleLogin = async () => {
  error.value = null;
  loading.value = true;
  try {
    // 1. ارسال درخواست POST به بک‌اند
    const response = await axios.post(`${API_URL}/login`, {
      username: username.value,
      password: password.value,
    });

    // 2. اگر موفق بود، توکن را در حافظه مرورگر ذخیره کن
    localStorage.setItem('crm-token', response.data.token);

    // 3. کاربر را به صفحه داشبورد بفرست
    router.push('/dashboard');

  } catch (err) {
    // 4. اگر خطا داد، پیام را نشان بده
    if (err.response && err.response.status === 401) {
      error.value = 'نام کاربری یا رمز عبور اشتباه است.';
    } else {
      error.value = 'خطا در برقراری ارتباط با سرور.';
    }
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* استایل‌های اختصاصی این صفحه */
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background-color: #f4f7f6;
}
.login-box {
  background: #ffffff;
  padding: 2.5rem;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
  width: 100%;
  max-width: 400px;
  text-align: right;
}
h2 {
  text-align: center;
  color: #333;
  margin-bottom: 2rem;
  font-weight: 700;
}
.input-group { margin-bottom: 1.5rem; }
.input-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #555;
}
.input-group input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-sizing: border-box; /* برای اینکه پدینگ عرض را خراب نکند */
  font-family: 'Vazirmatn', sans-serif;
  text-align: left; /* ورودی‌ها معمولا چپ‌چین هستند */
  direction: ltr;
}
.login-button {
  width: 100%;
  padding: 0.85rem;
  border: none;
  border-radius: 8px;
  background-color: #007bff;
  color: white;
  font-family: 'Vazirmatn', sans-serif;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease;
}
.login-button:hover { background-color: #0056b3; }
.login-button:disabled { background-color: #aaa; }
.error-message {
  color: #d93025;
  background-color: #fbeae9;
  border: 1px solid #f9d8d6;
  border-radius: 8px;
  padding: 0.75rem;
  margin-bottom: 1.5rem;
  text-align: center;
}
</style>

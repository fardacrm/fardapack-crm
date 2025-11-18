import axios from 'axios';

// ----------------------------------------------------------------------
// ✅ تنظیم آدرس API به صورت قطعی (Absolute URL) برای محیط پروداکشن
// ----------------------------------------------------------------------

// *** آدرس جدید سرویس Render شما: crm-6 ***
const RENDER_API_URL = 'https://fardapack-crm-6.onrender.com/api'; // <--- به‌روزرسانی نهایی به crm-6

// در محیط پروداکشن (بعد از npm run build) از آدرس کامل Render استفاده می‌شود.
// در محیط لوکال (npm run dev) از آدرس نسبی '/api' برای پروکسی استفاده می‌شود.
const BASE_URL = import.meta.env.PROD ? RENDER_API_URL : '/api';

const api = axios.create({
  baseURL: BASE_URL, 
  timeout: 15000, 
});

// تنظیم رهگیر برای ارسال توکن
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('crm-token');
    // توکن را به درخواست‌هایی که به /login ختم نمی‌شوند اضافه کن
    if (token && !config.url.endsWith('/login')) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// تنظیم رهگیر برای مدیریت خطاها
api.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        // اگر خطای 401 (غیرمجاز) بود، توکن را حذف و به صفحه اصلی هدایت کن
        if (error.response && error.response.status === 401) {
            localStorage.removeItem('crm-token');
            // از window.location.replace استفاده می‌کنیم تا تاریخچه مرورگر را تمیز کنیم
            if (window.location.pathname !== '/') {
                 window.location.replace('/'); 
            }
        }
        // اگر خطای شبکه یا خطای نامشخصی بود (که همان "خطا در برقراری ارتباط با سرور" را می‌دهد)
        if (!error.response || error.response.status >= 500) {
            console.error("Network Error or Server Down:", error);
            // می‌توانید یک پیام عمومی به کاربر نشان دهید
            // مثال: alert("خطا در برقراری ارتباط با سرور. لطفاً وضعیت سرویس را بررسی کنید.");
        }

        return Promise.reject(error);
    }
);

export default api;
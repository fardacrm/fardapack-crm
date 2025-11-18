import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import AppLayout from '../components/AppLayout.vue'
import DashboardView from '../views/DashboardView.vue'
import UsersView from '../views/UsersView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'login',
      component: LoginView
    },
    {
      path: '/app', 
      component: AppLayout, 
      meta: { requiresAuth: true },
      children: [
        {
          path: '/dashboard', 
          name: 'dashboard',
          component: DashboardView
        },
        {
          path: '/users',
          name: 'users',
          component: UsersView
        },
        
        // 💡 [جدید] مسیر پروفایل کاربر
        {
          path: '/users/:id', // :id یک پارامتر داینامیک است
          name: 'user-profile',
          component: () => import('../views/UserProfile.vue'),
        },
        
        {
          path: '/companies',
          name: 'companies',
          component: () => import('../views/CompaniesView.vue'),
        },
        
        // 💡 [جدید] مسیر پروفایل شرکت
        {
          path: '/companies/:id',
          name: 'company-profile',
          component: () => import('../views/CompanyProfile.vue'),
        },
        
        {
          path: '/calls',
          name: 'calls',
          component: () => import('../views/CallsView.vue'),
        },
        {
          path: '/followups',
          name: 'followups',
          component: () => import('../views/FollowupsView.vue'),
        },
        {
          path: '/orders',
          name: 'orders',
          component: () => import('../views/OrdersView.vue'),
        },
        {
          path: '/products',
          name: 'products',
          component: () => import('../views/ProductsView.vue'),
        },
        {
          path: '/admin',
          name: 'admin',
          component: () => import('../views/AdminView.vue'),
        }
      ]
    },
    {
      path: '/:catchAll(.*)',
      name: 'NotFound',
      component: () => import('../views/NotFoundView.vue')
    }
  ]
});

// گیت‌کیپر (بدون تغییر)
router.beforeEach((to, from, next) => {
    const isAuthenticated = localStorage.getItem('crm-token');
    
    // 💡 [اصلاح] چک کردن اینکه آیا مسیر به متا نیاز دارد یا خیر
    if (to.meta.requiresAuth && !isAuthenticated) {
        next({ name: 'login' });
    } else if (to.name === 'login' && isAuthenticated) {
        next({ name: 'dashboard' }); 
    } else {
        next();
    }
});

export default router
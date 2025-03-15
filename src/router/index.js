// src/router/index.js
//import Vue from 'vue';
import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../routes/HomePage.vue';
import UserLogin from '../routes/UserLogin.vue';
import UserRegister from '../routes/UserRegister.vue';
import ResetPassword from '../routes/ResetPassword.vue';
import Cookies from 'js-cookie';

//Vue.use(VueRouter);

const routes = [
  {
    path: '/',
    name: 'HomePage',
    component: HomePage
  },
  {
    path: '/Chat',
    name: 'Chat',
    component: HomePage
  },
  {
    path: '/UserLogin',
    name: 'UserLogin',
    component: UserLogin
  },
  {
    path: '/UserRegister',
    name: 'UserRegister',
    component: UserRegister
  },
  {
    path: '/ResetPassword',
    name: 'ResetPassword',
    component: ResetPassword
  },
];

const router = createRouter({
    history: createWebHistory(),
    routes
    });

    // 全局路由守卫
router.beforeEach((to, from, next) => {
    const isLoggedIn = Cookies.get('authToken') // 假设使用 'authToken' 存储登录状态
    if (!isLoggedIn && to.name !== 'UserLogin' && to.name !== 'UserRegister' && to.name !== 'ResetPassword') {
      next({ name: 'UserLogin' })
    } else {
      next()
    }
  })
  
export default router;
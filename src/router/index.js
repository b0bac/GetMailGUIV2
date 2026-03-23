import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Main',
    component: () => import('@/views/MainLayout.vue'),
    redirect: '/inbox',
    children: [
      {
        path: 'inbox',
        name: 'Inbox',
        component: () => import('@/views/Inbox.vue'),
        meta: { title: '收件箱' }
      },
      {
        path: 'compose',
        name: 'Compose',
        component: () => import('@/views/Compose.vue'),
        meta: { title: '写邮件' }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/Settings.vue'),
        meta: { title: '设置' }
      }
    ]
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' }
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title || 'GetMail'} - GetMail v2`
  
  const sessionId = localStorage.getItem('session_id')
  if (!sessionId && to.path !== '/login') {
    next('/login')
  } else if (to.path === '/login' && sessionId) {
    next('/')
  } else {
    next()
  }
})

export default router

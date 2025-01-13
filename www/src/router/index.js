import {createRouter, createWebHistory} from 'vue-router'


export const constantRouterMap = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/Layout'),
    children: [
      {
        path: '',
        name: '首页',
        component: () => import('@/views/DashBoard')
      },
      {
        path: '404',
        name: '404',
        component: () => import('@/views/errorPage/NotFound'),
      },
      {
        path: ':pathMatch(.*)*',
        name: '404',
        component: () => import('@/views/errorPage/NotFound'),
      },
    ]
  },
  {
    path: '/login',
    component: () => import('@/views/Login/index'),
    // hidden: true
  },
]

export default createRouter({
  history: createWebHistory(),
  // scrollBehavior: () => ({ y: 0 }),
  routes: constantRouterMap
})
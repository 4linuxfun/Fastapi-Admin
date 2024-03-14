import {createRouter, createWebHistory} from 'vue-router'


export const constantRouterMap = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/Layout'),
    children: []
  },
  {
    path: '/dashboard',
    component: () => import('@/views/Layout'),
    children: [
      {
        path: '',
        name: 'dashboard',
        component: () => import('@/views/DashBoard')
      }
    ]
  },
  {
    path: '/login',
    component: () => import('@/views/Login/index'),
    // hidden: true
  },
  // {
  //   path: '/404',
  //   name: 'notFound',
  //   component: () => import('@/views/errorPage/NotFound'),
  //   hidden: true
  // },
  // {
  //     path:'/:patchMatch(.*)*',
  //     name:'not-found',
  //     redirect:'/404'
  // }

  // {
  //   path: '/user',
  //   component: Layout,
  //   hidden: true,
  //   redirect: 'noredirect',
  //   children: [
  //     {
  //       path: 'center',
  //       component: () => import('@/views/system/user/center'),
  //       name: '个人中心',
  //       meta: { title: '个人中心', icon: 'user' }
  //     }
  //   ]
  // }
  // { path: '*', redirect: '/404', hidden: true }
]

export default createRouter({
  history: createWebHistory(),
  // scrollBehavior: () => ({ y: 0 }),
  routes: constantRouterMap
})
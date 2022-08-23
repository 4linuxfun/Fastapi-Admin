import router from './router';
import { useStore } from './stores';
import {
	getToken
} from '@/utils/auth';
import {
	makeRouter
} from "@/utils/router";


const whiteList = ['/login'] // no redirect whitelist

router.beforeEach((to) => {
	const store = useStore()
	console.log('start before each')

	if (getToken()) {
		console.log('已经有token')
		// 已登录且要跳转的页面是登录页
		if (to.path === '/login') {
			return '/dashboard'
		} else {
			console.log('已经登录成功')
			//登录成功，需要判断router是不是已经按照权限要求构建好，并且菜单是否按照权限要求生成，如没有，则生成
			// router.push('/')
			if (store.asyncRoutes.length === 0) {
				console.log('asyncroutes is not set')
				store.getInfo().then(() => {
					return store.getPermission()
				}).then(() => {
					let asyncRoutes = makeRouter(store.asyncRoutes)
					for (let route of asyncRoutes) {
						console.log('add route:')
						console.log(route)
						router.addRoute(route)
					}
					return { path: to.fullPath, replace: true }
				}).catch((err) => {
					console.log('用户权限拉取失败' + err);
					store.logOut().then(() => {
						location.reload()
					})
				})
			} else {
				console.log('当前生效路由表')
				console.log(router.getRoutes())
				return true
			}
		}
	} else {
		// 无token信息，表示未登录
		console.log('无token信息')
		if (whiteList.indexOf(to.path) !== -1) { // 在免登录白名单，直接进入
			return true
		} else {
			// return true
			router.push(`/login?redirect=${to.path}`) // 否则全部重定向到登录页
		}
	}
})

import {defineStore} from 'pinia'
import {
	requestLogin,
	requestGetInfo,
	requestPermission
} from '@/api/login'
import {
	getToken,
	setToken,
	removeToken
} from '@/utils/auth'

export const useStore = defineStore('user',{
	state:()=> {
		return {
			token: getToken(),
			name: "",
			email: '',
			avatar: '',
			roles: [],
			asyncRoutes: [],
		}
		
	},

	actions: {
		setToken(token) {
			this.token = token
		},
		setName(name) {
			this.name = name
		},
		setAvatar(avatar) {
			this.avatar = avatar
		},
		setRoles(roles) {
			this.roles = roles
		},
		setEmail(email) {
			this.email = email
		},
		setRouter(routers) {
			this.asyncRoutes = routers
		},
		//执行登录请求，获取token
		logIn(userInfo) {
			const username = userInfo.username
			const password = userInfo.password
			const rememberMe = userInfo.rememberMe
			console.log('user login actions')
			return new Promise((resolve, reject) => {
				requestLogin(username, password).then((response) => {
					console.log(response)
					setToken(response.token, rememberMe)
					this.setToken(response.token)
					resolve()
				}).catch((error) => {
					reject(error)
				})
			})
		},
		// 获取用户状态信息
		getInfo() {
			return new Promise((resolve, reject) => {
				console.log('get user info')
				requestGetInfo().then(response => {
					this.setRoles(response.roles)
					this.setName(response.username)
					this.setAvatar(response.avatar)
					this.setEmail(response.email)
					resolve(response)
				}).catch(error => {
					reject(error)
				})
			})
		},
		logOut() {
			return new Promise((resolve) => {
				this.setToken('')
				this.setRoles('')
				this.setRouter([])
				removeToken()
				resolve()
			})
		},
		// 获取用户权限列表
		getPermission() {
			return new Promise((resolve, reject) => {
				requestPermission().then(response => {
					console.log('permission response is:')
					console.log(response)
					this.setRouter(response)
					resolve(response)
				}).catch(error => {
					reject(error)
				})
			})
		}
	}
}
)
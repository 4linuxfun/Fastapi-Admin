import {
	createStore
} from 'vuex'
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

const store = createStore({
	state: {
		token: getToken(),
		name: "",
		email: '',
		avatar: '',
		roles: [],
		asyncRoutes: [],
	},
	getters: {
		asyncRoutes(state) {
			return state.asyncRoutes;
		},
	},
	mutations: {
		setToken(state, token) {
			state.token = token
		},
		setName(state, name) {
			state.name = name
		},
		setAvatar(state, avatar) {
			state.avatar = avatar
		},
		setRoles(state, roles) {
			state.roles = roles
		},
		setEmail(state, email) {
			state.email = email
		},
		setRouter(state, routers) {
			state.asyncRoutes = routers
		},
	},

	actions: {
		//执行登录请求，获取token
		logIn({
			commit
		}, userInfo) {
			const username = userInfo.username
			const password = userInfo.password
			const rememberMe = userInfo.rememberMe
			console.log('user login actions')
			return new Promise((resolve, reject) => {
				requestLogin(username, password).then((response) => {
					console.log(response)
					setToken(response.token, rememberMe)
					commit('setToken', response.token)
					resolve()
				}).catch((error) => {
					reject(error)
				})
			})
		},
		// 获取用户状态信息
		getInfo({
			commit
		}) {
			return new Promise((resolve, reject) => {
				console.log('get user info')
				requestGetInfo().then(response => {
					commit('setRoles', response.roles)
					commit('setName', response.username)
					commit('setAvatar', response.avatar)
					commit('setEmail', response.email)
					resolve(response)
				}).catch(error => {
					reject(error)
				})
			})
		},
		logOut({
			commit
		}) {
			return new Promise((resolve) => {
				commit('setToken', '')
				commit('setRoles', '')
				commit('setRouter', [])
				removeToken()
				resolve()
			})
		},
		// 获取用户权限列表
		getPermission({
			commit
		}) {
			return new Promise((resolve, reject) => {
				requestPermission().then(response => {
					console.log('permission response is:')
					console.log(response)
					commit('setRouter', response)
					resolve(response)
				}).catch(error => {
					reject(error)
				})
			})
		}
	}
})

export default store;

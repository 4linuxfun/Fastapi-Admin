import {defineStore} from 'pinia'
import {
  requestLogin,
  GetUserInfo,
  GetUserPermission
} from '@/api/users'
import {
  setToken,
  removeToken
} from '@/utils/auth'

export const useStore = defineStore('user', {
    state: () => {
      return {
        uid: '',
        token: '',
        name: '',
        avatar: '',
        asyncRoutes: [],
      }

    },
    getters: {
      buttons(state) {
        let btns = []

        function findAllBtn(list) {
          list.forEach(val => {
            if (val.type !== 'btn') {
              if (val.children && val.children.length > 0) {
                findAllBtn(val.children)
              }
            } else {
              btns.push(val.path)
            }
          })
        }

        findAllBtn(state.asyncRoutes)
        console.log('button:')
        console.log(btns)
        return btns
      },
    },

    actions: {
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
            this.token = response.token
            this.uid = response.uid
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
          GetUserInfo(this.uid).then(response => {
            this.name = response.name
            this.avatar = response.avatar
            resolve(response)
          }).catch(error => {
            reject(error)
          })
        })
      },
      logOut() {
        return new Promise((resolve) => {
          this.$reset()
          removeToken()
          resolve()
        })
      },
      // 获取用户权限列表
      getPermission() {
        return new Promise((resolve, reject) => {
          GetUserPermission().then(response => {
            console.log('permission response is:')
            console.log(response)
            this.asyncRoutes = response
            resolve(response)
          }).catch(error => {
            reject(error)
          })
        })
      }
    }
  }
)
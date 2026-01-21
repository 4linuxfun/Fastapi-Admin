import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  requestLogin,
  GetUserInfo,
  GetUserPermission
} from '@/api/users'
import {
  setToken,
  removeToken,
  getToken,
  setTokenWithRemember
} from '@/utils/auth'
import { useRouter } from 'vue-router'
import tokenManager from '@/utils/tokenManager'

export const useStore = defineStore('user', () => {

  const uid = ref('')
  const token = ref('')
  const name = ref(null)
  const avatar = ref(null)
  const asyncRoutes = ref([])
  const buttons = ref([])
  const router = useRouter()

  //执行登录请求，获取token
  function logIn(userInfo) {
    const username = userInfo.username
    const password = userInfo.password
    const rememberMe = userInfo.rememberMe
    console.log('user login actions')
    return new Promise((resolve, reject) => {
      requestLogin(username, password).then((response) => {
        console.log(response)
        setTokenWithRemember(response.token, rememberMe)
        token.value = response.token
        uid.value = response.uid
        
        // 重置token管理器
        tokenManager.reset()
        
        resolve()
      }).catch((error) => {
        reject(error)
      })
    })
  }

  // 获取用户状态信息
  function getInfo() {
    return new Promise((resolve, reject) => {
      console.log('get user info')
      GetUserInfo(this.uid).then(response => {
        name.value = response.name
        avatar.value = response.avatar
        resolve(response)
      }).catch(error => {
        reject(error)
      })
    })
  }

  function logOut() {
    return new Promise((resolve) => {
      // this.$reset()
      removeToken()
      
      // 停止token管理器
      tokenManager.stop()
      
      uid.value = ''
      token.value = ''
      name.value = null
      avatar.value = null
      asyncRoutes.value = []
      buttons.value = []
      router.push('/login')
      resolve()
    })
  }

  // 获取用户权限列表
  function getPermission() {
    return new Promise((resolve, reject) => {
      GetUserPermission().then(response => {
        console.log('permission response is:')
        console.log(response)
        asyncRoutes.value = (response.menus)
        buttons.value = (response.btns)
        resolve(response)
      }).catch(error => {
        reject(error)
      })
    })
  }

  return { uid, token, name, avatar, asyncRoutes, buttons, getInfo, logIn, logOut, getPermission }
}
)
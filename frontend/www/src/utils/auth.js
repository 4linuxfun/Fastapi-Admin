import Cookies from 'js-cookie'
import { refreshToken } from '@/api/users'
import { ElNotification } from 'element-plus'

const TokenKey = 'Token'
const TokenRefreshKey = 'TokenRefreshTime'

// token刷新状态管理
let isRefreshing = false
let refreshPromise = null

export function getToken() {
  return Cookies.get(TokenKey)
}

export function setToken(token, rememberMe) {
  if (rememberMe) {
    return Cookies.set(TokenKey, token, { expires: 1 })
  } else {
    return Cookies.set(TokenKey, token)
  }
}

export function removeToken() {
  Cookies.remove(TokenKey)
  Cookies.remove(TokenRefreshKey)
  return true
}

/**
 * 检查token是否需要刷新
 * @returns {boolean}
 */
export function shouldRefreshToken() {
  const token = getToken()
  if (!token) return false
  
  try {
    // 解析JWT token获取过期时间
    const payload = JSON.parse(atob(token.split('.')[1]))
    const exp = payload.exp * 1000 // 转换为毫秒
    const now = Date.now()
    const timeUntilExpiry = exp - now
    
    // 如果剩余时间少于5分钟（300000毫秒），需要刷新
    return timeUntilExpiry < 300000 && timeUntilExpiry > 0
  } catch (error) {
    console.error('Token解析失败:', error)
    return true
  }
}

/**
 * 自动刷新token
 * @param {boolean} force - 是否强制刷新，忽略shouldRefreshToken检查
 * @returns {Promise<boolean>}
 */
export async function autoRefreshToken(force = false) {
  // 如果正在刷新，返回现有的Promise
  if (isRefreshing && refreshPromise) {
    return refreshPromise
  }
  
  // 检查是否需要刷新（除非强制刷新）
  if (!force && !shouldRefreshToken()) {
    return true
  }
  
  // 检查最近是否已经刷新过（避免频繁刷新）
  const lastRefreshTime = Cookies.get(TokenRefreshKey)
  if (lastRefreshTime && Date.now() - parseInt(lastRefreshTime) < 60000) { // 1分钟内不重复刷新
    return true
  }
  
  isRefreshing = true
  
  refreshPromise = new Promise(async (resolve) => {
    try {
      console.log('开始自动刷新token...')
      const response = await refreshToken()
      
      if (response && response.token) {
        // 更新token
        const rememberMe = Cookies.get(TokenKey + '_remember') === 'true'
        setTokenWithRemember(response.token, rememberMe)
        
        // 记录刷新时间
        Cookies.set(TokenRefreshKey, Date.now().toString())
        
        console.log('Token刷新成功')
        resolve(true)
      } else {
        console.error('Token刷新失败：响应格式错误')
        resolve(false)
      }
    } catch (error) {
      console.error('Token刷新失败:', error)
      
      // 如果是401错误，说明token已完全过期，需要重新登录
      if (error.response && error.response.status === 401) {
        ElNotification({
          title: '提示',
          message: '登录已过期，请重新登录',
          type: 'warning'
        })
        removeToken()
        window.location.href = '/login'
      }
      
      resolve(false)
    } finally {
      isRefreshing = false
      refreshPromise = null
    }
  })
  
  return refreshPromise
}

/**
 * 设置token并记住登录状态
 * @param {string} token 
 * @param {boolean} rememberMe 
 */
export function setTokenWithRemember(token, rememberMe) {
  setToken(token, rememberMe)
  // 记录是否选择了记住登录
  Cookies.set(TokenKey + '_remember', rememberMe.toString())
}
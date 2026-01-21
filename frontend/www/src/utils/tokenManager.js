import { autoRefreshToken, shouldRefreshToken, getToken } from '@/utils/auth'
import { ElNotification } from 'element-plus'

class TokenManager {
  constructor() {
    this.refreshTimer = null
    this.checkInterval = 60000 // 每分钟检查一次
    this.isActive = false
  }

  /**
   * 启动token管理器
   */
  start() {
    if (this.isActive) return
    
    this.isActive = true
    console.log('Token管理器已启动')
    
    // 立即检查一次
    this.checkAndRefresh()
    
    // 设置定时检查
    this.refreshTimer = setInterval(() => {
      this.checkAndRefresh()
    }, this.checkInterval)
    
    // 监听页面可见性变化，当页面重新可见时检查token
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden && this.isActive) {
        this.checkAndRefresh()
      }
    })
  }

  /**
   * 停止token管理器
   */
  stop() {
    if (!this.isActive) return
    
    this.isActive = false
    console.log('Token管理器已停止')
    
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer)
      this.refreshTimer = null
    }
  }

  /**
   * 检查并刷新token
   */
  async checkAndRefresh() {
    if (!this.isActive) return
    
    const token = getToken()
    if (!token) {
      this.stop()
      return
    }

    try {
      if (shouldRefreshToken()) {
        console.log('检测到token即将过期，开始自动刷新...')
        const success = await autoRefreshToken()
        
        if (success) {
          console.log('Token自动刷新成功')
        } else {
          console.error('Token自动刷新失败')
          this.handleRefreshFailure()
        }
      }
    } catch (error) {
      console.error('Token检查过程中发生错误:', error)
      this.handleRefreshFailure()
    }
  }

  /**
   * 处理刷新失败
   */
  handleRefreshFailure() {
    ElNotification({
      title: '提示',
      message: 'Token刷新失败，请重新登录',
      type: 'warning',
      duration: 5000
    })
    
    // 停止管理器，避免继续尝试
    this.stop()
  }

  /**
   * 重置管理器（用于重新登录后）
   */
  reset() {
    this.stop()
    setTimeout(() => {
      this.start()
    }, 1000) // 延迟1秒后重新启动
  }
}

// 创建全局实例
const tokenManager = new TokenManager()

export default tokenManager
import { ref, computed } from 'vue'
import { getToken } from '@/utils/auth'
import { ElNotification } from 'element-plus'

export function useUpload() {
  const uploadUrl = ref('/api/upload')
  
  const headers = computed(() => {
    return { Authorization: 'Bearer ' + getToken() }
  })

  /**
   * 通用上传成功处理函数
   * @param {Object} response - API 响应对象
   * @returns {Array<string>|null} - 成功返回 URL 数组，否则返回 null
   */
  const handleUploadSuccess = (response) => {
    if (response.data && response.data.urls && response.data.urls.length > 0) {
        return response.data.urls
    }
    ElNotification.error('上传失败: 未能获取文件地址')
    return null
  }

  const handleUploadError = (err) => {
    console.error(err)
    ElNotification.error('上传出错')
  }

  return {
    uploadUrl,
    headers,
    handleUploadSuccess,
    handleUploadError
  }
}

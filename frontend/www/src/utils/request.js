import axios from 'axios'
// import { Notification, detailBox } from 'element-ui'
import { useStore } from '../stores'
import { getToken, autoRefreshToken } from '@/utils/auth'
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'
import { DelJob } from '@/api/jobs'

// 创建axios实例
const service = axios.create({
  baseURL: import.meta.env.VITE_APP_BASEURL, // api 的 base_url
  timeout: 60000 // 请求超时时间
})

// request拦截器，用于添加HTTP header：Authorization，所有的数据请求类型都是json
service.interceptors.request.use(
  async config => {
    console.log('请求拦截')
    
    // 跳过token刷新接口的自动刷新检查，避免循环调用
    if (config.url !== '/api/refresh' && getToken()) {
      // 自动检查并刷新token
      await autoRefreshToken()
    }
    
    if (getToken()) {
      config.headers['Authorization'] = 'Bearer ' + getToken() // 让每个请求携带自定义token 请根据实际情况自行修改
    }
    // config.headers['Content-Type'] = 'application/json'
    if (config.data !== undefined) {
      if (config.data.excu !== undefined) {
        if (config.data.excu === 'tail_start') {
          config.timeout = 60000 * 20
        } else {
          config.timeout = 20000
        }
      }
    }
    return config
  },
  error => {
    // Do something with request error
    console.log(error) // for debug
    Promise.reject(error)
  }
)

// response 拦截器
service.interceptors.response.use(
  response => {
    // 内部服务状态码
    console.log('拦截器')
    // 需要添加下载类型是否为文件，文件不走通用的返回类型
    // console.log(response.headers)
    const disposition = response.headers['content-disposition'] || response.headers['Content-Disposition']
    if (disposition) {
      let filename = ''
      const utf8FilenameRegex = /filename\*=UTF-8''([\w%\-\.]+)/i
      const asciiFilenameRegex = /filename="?([^"]+)"?/i

      const utf8Matches = disposition.match(utf8FilenameRegex)
      if (utf8Matches && utf8Matches[1]) {
        filename = decodeURIComponent(utf8Matches[1])
      } else {
        const asciiMatches = disposition.match(asciiFilenameRegex)
        if (asciiMatches && asciiMatches[1]) {
          filename = asciiMatches[1]
        }
      }

      return {
        type: 'file',
        data: response.data,
        filename
      }
    }
    if (response.data.code >= 200 && response.data.code < 300) {
      return response.data.data
    } else {
      console.log('response error')
      ElNotification({
        title: '错误',
        message: response.data.message,
        type: 'error'
      })
      return Promise.reject()
    }
  },
  error => {
    const code = error.response?.status
    console.log('error code:' + code)
    if (code === 401) {
      const store = useStore()
      ElNotification({
        title: 'Error',
        message: '登录超时，需要重新登录',
        type: 'error',
      })
      store.logOut().then(() => {
        window.location.reload() // 为了重新实例化vue-router对象 避免bug
      })
    } else {
      ElNotification({
        title: '错误',
        type: 'error',
        message: error.response.data,
        duration: 10000
      })
    }
    return Promise.reject(error)
  }
)

export function GET(url, params, isFile = false) {
  return service({
    url,
    params,
    method: 'get',
    responseType: isFile ? 'arraybuffer' : 'json'
  })
}

export function POST(url, data, config = {}) {
  return service({
    url,
    data,
    method: 'post',
    ...config
  })
}


export function PUT(url, data) {
  return service({
    url,
    data,
    method: 'put'
  })
}

export function DELETE(url, params) {
  return service({
    url,
    params,
    method: 'delete'
  })
}

/**
 * 删除确认对话框，可以直接提供func和对应id
 * @returns {Promise<unknown>}
 * @constructor
 * @param txt 提示信息
 * @param func 执行函数
 * @param id 执行ID
 */
export function ConfirmDel(txt, func, id) {
  return ElMessageBox.confirm(txt, '警告', { type: 'warning' })
    .then(() => func(id))
    .then(() => {
      ElMessage({
        title: 'success',
        message: '删除成功',
        type: 'success'
      })
    })
    .catch((error) => {
      if (error !== 'cancel') {
        ElMessage({
          title: 'success',
          message: '删除失败',
          type: 'warning'
        })
        throw error
      }

    })

}

export default service
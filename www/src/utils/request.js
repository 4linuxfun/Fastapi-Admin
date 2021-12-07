import axios from 'axios'
import router from '@/router'
// import { Notification, detailBox } from 'element-ui'
import {useStore} from '../stores'
import {getToken} from '@/utils/auth'
import { ElNotification } from 'element-plus'

// 创建axios实例
const service = axios.create({
    baseURL: 'http://localhost', // api 的 base_url
    timeout: 60000 // 请求超时时间
})

// request拦截器，用于添加HTTP header：Authorization，所有的数据请求类型都是json
service.interceptors.request.use(
    config => {
        console.log('请求拦截')
        if (getToken()) {
            config.headers['Authorization'] = 'Bearer ' + getToken() // 让每个请求携带自定义token 请根据实际情况自行修改
        }
        config.headers['Content-Type'] = 'application/json'
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
		if ("content-disposition" in response.headers){
			let filename = ""
			let disposition = response.headers['content-disposition']
			// 下载文件名的几种获取方式，暂时不够完美，而且中文没有解码
			let result = disposition.match(/filename="(.*)"/)
			let result2 = disposition.match(/filename\*=(.*?)''(.*$)/)
			// console.log('result:'+result)
			// console.log('result2:'+ result2)
			if (result !== null){
				
				filename = result[1]	
			}
			if (result2 !== null){
				
				filename = result2[2]
			}
			console.log('filename:'+filename)
			return {
				data:response.data,
				filename
			}
		}
		const code = response.data.code
		if(code != 0){
			return Promise.reject(response.data.data)
		} else {
            return response.data.data
        }
    },
    error => {
        let code = 0
        console.log('返回错误：'+error)
        try {
            code = error.response.status
        } catch (e) {
            if (error.toString().indexOf('timeout')) {
                ElNotification({
                    title: '错误',
                    message: '请求超时!',
					type:'error'
                })
                return Promise.reject(error)
            }
        }
		console.log('error code:'+code)
        if (code === 401) {
			const store = useStore()
            ElNotification({
                    title: 'Error',
                    message: '登录超时，需要重新登录',
                    type: 'error',
                  })
			store.logOut().then(() => {
				window.location.reload(); // 为了重新实例化vue-router对象 避免bug
			})
        } else if (code === 403) {
            router.push({path: '/401'})
        } else if (code === 502) {
            ElNotification({
                title: '错误',
                type: 'error',
                message: '后端服务器连接失败!'
            })
        } else {
            const errorMsg = error.response.data
            if (errorMsg !== undefined) {
                ElNotification({
                    title: '错误',
                    type: 'error',
                    message: errorMsg,
                    duration: 2500
                })
            }
        }
        return Promise.reject(error)
    }
)
export default service
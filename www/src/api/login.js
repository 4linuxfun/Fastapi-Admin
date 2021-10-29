import request from '@/utils/request'

export function requestLogin(username, password) {
  console.log('do login url post')
  return request({
    url: 'api/user/login',
    method: 'post',
    data: {
      username,
      password
    }
  })
}

export function requestGetInfo() {
  return request({
    url: 'api/user/user_info',
    method: 'get'
  })
}

export function requestPermission() {
  return request({
    url: 'api/user/permission',
    method: 'get'
  })
}
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

export function requestUsers() {
  return request({
    url: 'api/user/all',
    method: 'get'
  })
}

export function requestUserRoles(userId){
	return request({
		url:'api/user/role_list/',
		params:{
			id:userId
		},
		method:'get'
	})
}


export function requestUpdateUser(user, roles) {
  return request({
    url: 'api/user/update',
    method: 'post',
    data: {
      user,
      roles
    }
  })
}

export function requestDelUser(userId){
	return request({
		url:'api/user/del/'+userId,
		method:'get'
	})
}
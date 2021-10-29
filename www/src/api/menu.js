// menu相关的API
import request from '@/utils/request'

export function requestGetAllMenu(){
	console.log('request all menu list')
	return request({
		url: 'api/menu/all',
		method: 'get',
	})
}


export function requestUpdateMenu(menuInfo) {
	console.log('update menu request')
	return request({
		url: 'api/menu/update',
		method: 'post',
		data: menuInfo,
	})
}

export function requestDelMenu(id) {
	return request({
		url: 'api/menu/del/'+id,
		method: 'get',
	})
}


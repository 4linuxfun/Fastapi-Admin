import request from '@/utils/request'

export function requestRoles() {
	// 获取所有的角色列表
	return request({
		url: 'api/role/all',
		method: 'get',
	})
}

export function requestRoleInfo(roleId) {
	// 获取指定roleId的信息
	return request({
		url: 'api/role/'+roleId,
		method: 'get',
	})
}

export function requestRoleMenus(roleId) {
	// 通过roleid获取对应角色的所有菜单权限列表
	return request({
		url: 'api/role/menus/',
		params: {
			id: roleId
		},
		method: 'get',
	})
}

export function requestUpdateRoles(role, menuList,category) {
	// 更新角色的权限
	return request({
		url: 'api/role/update',
		method: 'post',
		data: {
			role: role,
			menus: menuList,
			category: category
		}
	})
}

export function requestDelRole(roleId){
	return request({
		url: 'api/role/del/'+roleId,
		method: 'get',
	})
}

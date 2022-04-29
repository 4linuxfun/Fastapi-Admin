import {GET, POST, PUT, DELETE} from '@/utils/request'

// 角色接口
export const GetRoles = (q) => GET('api/roles', {q})
export const GetRoleInfo = (roleId) => GET('api/roles' + roleId)
export const GetRoleEnableMenus = (roleId) => GET('api/roles/enable-menus', {id: roleId})
export const PostNewRoles = (role) => POST('api/roles', role)
export const PutRoles = (role) => PUT('api/roles', role)
export const DeleteRole = (roleId) => DELETE('api/roles/' + roleId)
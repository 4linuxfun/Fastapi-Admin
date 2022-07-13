import {GET, POST, PUT, DELETE} from '@/utils/request'

// 用户相关接口
export const requestLogin = (username, password) => POST('/api/login', {username, password})
export const GetUserInfo = (uid) => GET('/api/users/' + uid)
export const GetUserPermission = () => GET('/api/permission')
export const GetUserExist = (name) => GET('/api/users/exist', {name})
export const GetUserRoles = (userId) => GET('/api/users/roles', {id: userId})
export const PutNewUser = (user, roles) => PUT('/api/users/' + user.id, {user, roles})
export const PostAddUser = (user, roles) => POST('/api/users', {user, roles})
export const DeleteUser = (userId) => DELETE('/api/users/' + userId)
export const ResetPasswd = (userId, password) => PUT('/api/users/password', {id: userId, password})
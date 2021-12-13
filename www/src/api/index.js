import {GET,POST,PUT,DELETE} from '@/utils/request'
import { Base64 } from 'js-base64'

// 用户相关接口
export const requestLogin = (username, password) => POST('api/login',{username,password})
export const GetUserInfo = (uid)=> GET('api/users/'+uid)
export const GetUserPermission = ()=>GET('api/permission')
export const GetUsers = () => GET('api/users')
export const GetUserRoles = (userId) => GET('api/users/roles',userId)  
export const PutNewUser = (user, roles) => PUT('api/users/'+user.id,{user,roles})
export const PostAddUser = (user,roles) =>POST('api/users',{user,roles})
export const DeleteUser = (userId) => DELETE('api/users'+userId)

export const SearchCategoryFields = (category_id, query) =>GET('/api/fields',{category_id,query})

// 菜单接口
export const GetAllMenus = ()=>GET('api/menus')
export const PostNewMenu = (menuInfo) =>POST('api/menus',menuInfo)
export const PutMenu = (menuInfo) =>PUT('api/menus',menuInfo)
export const DeleteMenu = (id)=>DELETE('api/menus/'+id)

// 角色接口
export const GetRoles = ()=>GET('api/roles')
export const GetRoleInfo = (roleId)=>GET('api/roles'+roleId)
export const GetRoleEnableMenus = (roleId) =>GET('api/roles/enable-menus/',{id:roleId})
export const PostNewRoles = (role, menuList,category)=>POST('api/roles',{role,menus:menuList,category})
export const PutRoles = (role, menuList,category)=>PUT('api/roles',{role,menus:menuList,category}) 
export const DeleteRole = (roleId)=>DELETE('api/roles/'+roleId)
export const GetRoleCategories = (id)=>GET('api/roles/categories',{id})

// 资产类别接口
export const GetCategories = (search) =>GET('api/categories',{search})
export const GetCategoryDetail = (id) =>GET('api/categories/'+id +'/detail')
export const GetCategoryFields = (id) =>GET('api/categories/'+id+'/fields')
export const PostCategory = (category) => POST('api/categories',category)

// 资产接口
export const GetAssets = (q) =>GET('api/assets',{q:Base64.encode(JSON.stringify(q))})
export const GetAssetsCount = (q) =>GET('api/assets/count', {q:Base64.encode(JSON.stringify(q))})
export const PostAssets = (assets)=>POST('api/assets',assets)
export const PutAssets = (fields)=>PUT('api/assets',fields)
export const PutAssetsMulti = (updateInfo) => PUT('api/assets/multi',updateInfo)

// 文件操作接口
export const ImportFile = (data)=>POST('api/assets/system/import',data)

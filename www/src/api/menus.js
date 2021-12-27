import { GET, POST, PUT, DELETE } from '@/utils/request'

// 菜单接口
export const GetAllMenus = (q) => GET('api/menus', { q })
export const PostNewMenu = (menu) => POST('api/menus', menu )
export const PutMenu = (menu) => PUT('api/menus', menu)
export const DeleteMenu = (id) => DELETE('api/menus/' + id)
export const GetMenuApis = (id) => GET('api/menus/' + id + '/apis')
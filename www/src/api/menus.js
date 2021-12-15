import { GET, POST, PUT, DELETE } from '@/utils/request'

// 菜单接口
export const GetAllMenus = (q) => GET('api/menus', { q })
export const PostNewMenu = (menuInfo) => POST('api/menus', menuInfo)
export const PutMenu = (menuInfo) => PUT('api/menus', menuInfo)
export const DeleteMenu = (id) => DELETE('api/menus/' + id)
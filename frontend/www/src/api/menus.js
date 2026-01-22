import { GET, POST, PUT, DELETE } from '@/utils/request'

// 菜单接口
export const GetAllMenus = () => GET('/api/menus')
export const PostNewMenu = (menu) => POST('/api/menus', menu )
export const PutMenu = (menu) => PUT('/api/menus', menu)
export const DeleteMenu = (id) => DELETE('/api/menus/' + id)
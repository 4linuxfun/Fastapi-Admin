import { GET, POST, PUT, DELETE } from '@/utils/request'
// sys_api表相关接口

export const GetApis = (q) => GET('api/sys-apis', { q })
export const PostApis = (api) => POST('api/sys-apis', api)
export const PutApis = (api) => PUT('api/sys-apis', api)
export const DelApis = (id) => DELETE('api/sys-apis/' + id)
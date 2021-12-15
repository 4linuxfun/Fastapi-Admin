import {GET} from '@/utils/request'
// sys_api表相关接口

export const GetApis = (q)=>GET('api/sys-apis',{q})
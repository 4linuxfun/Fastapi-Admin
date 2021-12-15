import {GET,POST,PUT} from '@/utils/request'
import {Base64} from 'js-base64'

// 资产接口
export const GetAssets = (q) =>GET('api/assets',{q:Base64.encode(JSON.stringify(q))})
export const GetAssetsCount = (q) =>GET('api/assets/count', {q:Base64.encode(JSON.stringify(q))})
export const PostAssets = (assets)=>POST('api/assets',assets)
export const PutAssets = (fields)=>PUT('api/assets',fields)
export const PutAssetsMulti = (updateInfo) => PUT('api/assets/multi',updateInfo)

// 文件操作接口
export const ImportFile = (data)=>POST('api/assets/system/import',data)
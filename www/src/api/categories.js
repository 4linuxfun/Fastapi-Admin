import {GET,POST,PUT} from '@/utils/request'

// 资产类别接口
export const GetCategories = (search) =>GET('api/categories',{search})
export const GetCategoryDetail = (id) =>GET('api/categories/'+id +'/detail')
export const GetCategoryFields = (id) =>GET('api/categories/'+id+'/fields')
export const PostCategory = (category) => POST('api/categories',category)
export const PutCategory = (id,category) => PUT('api/categories/'+id,category)
import { GET, POST, PUT, DELETE } from '@/utils/request'

export const GetCategoryTree = (search) => GET('/api/category/tree', search)
export const AddNewCategory = (category) => POST('/api/category', category)
export const UpdateCategory = (category) => PUT('/api/category', category)
export const LogicalDeleteCategory = (categoryId) => DELETE('/api/category/logical/' + categoryId)
import { GET } from '@/utils/request'

export const SearchCategoryFields = (category_id, query) => GET('/api/assets/category/fields', { category_id, query })
import { GET } from '@/utils/request'

export const SearchCategoryFields = (category_id, query) => GET('/api/fields', { category_id, query })
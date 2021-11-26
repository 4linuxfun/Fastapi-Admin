import request from '@/utils/request'


export function requestCategoryField(category_id, query) {
	return request({
		url: '/api/assets/category_field',
		method: 'get',
		params: {
			category_id: category_id,
			query: query
		}
	})
}

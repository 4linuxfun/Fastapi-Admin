import {
	ref,
	watch
} from 'vue'

export default function usePagination(searchFunc) {
	const search = ref(null)
	const tableData = ref([])
	const pageSize = ref(10)
	const currentPage = ref(1)
	const total = ref(0)
	const lastId = ref(0)
	const firstId = ref(0)

	// 初始化调用
	searchFunc(search.value, 'next', lastId.value, pageSize.value, null).then((response) => {
		tableData.value = response.data
		total.value = response.total
		updateFirstLastId()
	})

	const updateFirstLastId = () => {
		let idArray = []
		tableData.value.forEach(item => {
			idArray.push(item.id)
		})
		idArray.sort((a, b) => a - b)
		console.log(idArray)
		firstId.value = idArray[0]
		// slice返回为array
		lastId.value = idArray.slice(-1)[0]
		console.log(firstId.value, lastId.value)
	}

	const freshCurrentPage = () => {
		searchFunc(search.value, 'current', firstId.value, pageSize.value).then((response) => {
			tableData.value = response.data
			total.value = response.total
			updateFirstLastId()
		})

	}
	const handleSearch = () => {
		currentPage.value = 1
		searchFunc(search.value, 'current', null, pageSize.value).then((response) => {
			tableData.value = response.data
			total.value = response.total
			updateFirstLastId()
		})
	}

	watch(currentPage, (newValue, oldValue) => {
		console.log(newValue)
		if ((newValue - oldValue) == 1) {
			console.log('下一页')
			searchFunc(search.value, 'next', lastId.value, pageSize.value, null).then((response) => {
				tableData.value = response.data
				total.value = response.total
				updateFirstLastId()
			})
		} else if ((newValue - oldValue) > 1) {
			console.log('向后跳页:' + newValue)
			searchFunc(search.value, 'next_page', lastId.value, pageSize.value, newValue - oldValue).then((
				response) => {
				tableData.value = response.data
				total.value = response.total
				updateFirstLastId()
			})
		} else if ((newValue - oldValue) < -1) {
			console.log('向前跳页：' + newValue)
			searchFunc(search.value, 'prev_page', lastId.value, pageSize.value, oldValue - newValue).then((
				response) => {
				tableData.value = response.data
				total.value = response.total
				updateFirstLastId()
			})
		} else {
			console.log('上一页')
			searchFunc(search.value, 'prev', firstId.value, pageSize.value).then((response) => {
				tableData.value = response.data
				total.value = response.total
				updateFirstLastId()
			})
		}
	})
	watch(pageSize, (newValue) => {
		// pageSize变更后，为了保障页数等信息，最好还是返回第一页
		console.log('pagesize：' + newValue)
		searchFunc(search.value, 'current', firstId.value, pageSize.value).then((response) => {
			tableData.value = response.data
			total.value = response.total
			updateFirstLastId()
		})
	})
	return {
		search,
		tableData,
		currentPage,
		pageSize,
		total,
		firstId,
		lastId,
		freshCurrentPage,
		handleSearch
	}
}

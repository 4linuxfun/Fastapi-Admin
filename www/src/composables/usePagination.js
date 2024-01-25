import {
  reactive,
  ref,
  watch
} from 'vue'
import {POST} from '@/utils/request'

export default function usePagination(url, searchForm, orderType = 'asc') {
  const search = reactive(searchForm)
  const tableData = ref([])
  const pageSize = ref(10)
  const currentPage = ref(1)
  const orderModel = ref(orderType)
  const total = ref(0)


  const searchFunc = (search, page, pageSize, orderModel) => POST(url, {
    search,
    page,
    page_size: pageSize,
    model:orderModel
  })
  // // 初始化调用
  // searchFunc(search, currentPage.value, pageSize.value, orderModel.value).then((response) => {
  //   tableData.value = response.data
  //   total.value = response.total
  // })

  const freshCurrentPage = () => {
    searchFunc(search, currentPage.value, pageSize.value, orderModel.value).then((response) => {
      tableData.value = response.data
      total.value = response.total
    })

  }
  const handleSearch = () => {
    currentPage.value = 1
    searchFunc(search, currentPage.value, pageSize.value, orderModel.value).then((response) => {
      tableData.value = response.data
      total.value = response.total
    })
  }

  watch(currentPage, (newValue, oldValue) => {
    console.log(newValue)
    searchFunc(search, currentPage.value, pageSize.value, orderModel.value).then((
      response) => {
      tableData.value = response.data
      total.value = response.total
    })

  })
  watch(pageSize, (newValue) => {
    // pageSize变更后，为了保障页数等信息，最好还是返回第一页
    console.log('pagesize：' + newValue)
    searchFunc(search, currentPage.value, pageSize.value, orderModel.value).then((
      response) => {
      tableData.value = response.data
      total.value = response.total
    })
  })
  return {
    search,
    tableData,
    currentPage,
    pageSize,
    orderModel,
    total,
    freshCurrentPage,
    handleSearch
  }
}

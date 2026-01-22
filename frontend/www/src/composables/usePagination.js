import { reactive, ref, watch } from 'vue'
import { POST } from '@/utils/request'

/**
 * 分页逻辑复用函数
 * @param {string} url - 请求的API地址
 * @param {Object} searchForm - 搜索表单数据，默认为空对象
 * @param {string} orderType - 排序方式，默认为 'asc'
 * @param {number} initialPageSize - 每页显示条数，默认为 10
 * @returns {Object} - 返回分页相关的状态和方法
 */
export default function usePagination(url, searchForm = {}, orderType = 'asc', initialPageSize = 10) {
  // 响应式搜索表单数据
  const search = reactive(searchForm)

  // 表格数据
  const tableData = ref([])

  // 每页显示条数
  const pageSize = ref(initialPageSize)

  // 当前页码
  const currentPage = ref(1)

  // 排序方式
  const orderModel = ref(orderType)

  // 数据总数
  const total = ref(0)

  // loading状态
  const loading = ref(false)

  /**
   * 获取分页数据
   * @returns {Promise<void>}
   */
  const fetchData = async () => {
    loading.value = true
    const response = await POST(url, {
      search,
      page: currentPage.value,
      page_size: pageSize.value,
      model: orderModel.value,
    })
    tableData.value = response.data
    total.value = response.total
    loading.value = false
  }

  /**
   * 刷新当前页数据
   */
  const freshCurrentPage = async () => {
    await fetchData()
  }

  /**
   * 处理搜索操作，重置页码并获取数据
   */
  const handleSearch = async () => {
    currentPage.value = 1
    await fetchData()
  }

  function setLodding(value) {
    loading.value = value
  }

  // 监听 currentPage 和 pageSize 的变化，自动获取数据
  watch([currentPage, pageSize], async () => {
    await fetchData()
  })

  // 返回分页相关的状态和方法
  return {
    search,
    tableData,
    currentPage,
    pageSize,
    orderModel,
    total,
    loading,
    freshCurrentPage,
    handleSearch,
  }
}

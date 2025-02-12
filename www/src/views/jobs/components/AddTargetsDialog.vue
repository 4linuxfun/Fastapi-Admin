<!--弹出dialog，方便用户批量选择主机-->
<template>
  <el-dialog v-model="visible" title="主机列表" width="70%">
    <div style="background-color: rgb(240, 242, 245)">
      <el-row :gutter="10">
        <el-col :span="8">
          <el-tree ref="elTreeRef" :data="allGroups" :props="{label:'name'}"
                   style="height: 100%;margin: 10px 0 0 10px;" highlight-current default-expand-all
                   :expand-on-click-node="false"
                   @node-click="handleNodeClick"
          />
        </el-col>
        <el-col :span="16">
          <el-input v-model="search.name" placeholder="请输入主机名" style="width: 100%;margin: 10px 10px 10px 0"
                    clearable
                    @change="handleSearch"/>
          <el-table ref="tableRef" :data="tableData" border style="margin-top: 10px"
                    @select="handleSelect"
                    @select-all="handleSelectAll">
            <el-table-column type="selection" label="#" align="center"/>
            <el-table-column prop="name" label="主机名" align="center"/>
            <el-table-column prop="ansible_host" label="主机IP" align="center"/>
            <el-table-column prop="ansible_port" label="主机端口" align="center"/>
            <el-table-column prop="desc" label="描述" align="center"/>
          </el-table>
          <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total" background
                         layout="total,prev,pager,next,sizes,jumper"
                         style="margin-top: 10px;"
          />
          <el-button style="margin: 10px" @click="visible = false">取消</el-button>
          <el-button type="primary" @click="handleAdd">确定</el-button>

        </el-col>
      </el-row>
    </div>

  </el-dialog>
</template>

<script setup>
  import {ref, watch, nextTick} from 'vue'
  import {GetAllGroup} from '@/api/host.js'
  import usePagination from '@/composables/usePagination.js'

  const emit = defineEmits(['success'])
  const tableRef = ref(null)
  const visible = ref(false)
  const allGroups = ref([])
  const selectedHosts = ref([])
  const isProgramSelect = ref(false)

  const searchForm = {
    name: null,
    ansible_host: null,
    group_id: null,
    ancestors: null
  }
  const {
    search,
    tableData,
    currentPage,
    pageSize,
    orderModel,
    total,
    freshCurrentPage,
    handleSearch
  } = usePagination('/api/host/search', searchForm)

  function handleNodeClick(data) {
    search.group_id = data.id
    search.ancestors = data.ancestors
    handleSearch()
  }

  /**
   *增加主机
   */
  function handleAdd() {
    console.log(selectedHosts.value)
    visible.value = false
    emit('success', selectedHosts.value)
  }

  /**
   * 处理单行选择
   */
  function handleSelect(selection, row) {
    console.log('handleSelect', selection, row)
    if (isProgramSelect.value) {
      isProgramSelect.value = false
      return
    }

    // 检查是选中还是取消选中
    const isSelected = selection.some(item => item.id === row.id)
    if (isSelected) {
      // 添加新选择的主机
      if (!selectedHosts.value.some(host => host.id === row.id)) {
        selectedHosts.value.push(row)
      }
    } else {
      // 移除取消选择的主机
      selectedHosts.value = selectedHosts.value.filter(host => host.id !== row.id)
    }
    console.log('selectedHosts', selectedHosts.value)
  }

  /**
   * 处理全选
   */
  function handleSelectAll(selection) {
    console.log('handleSelectAll', selection)
    if (isProgramSelect.value) {
      isProgramSelect.value = false
      return
    }

    // 获取当前页面上的所有主机ID
    const currentPageIds = tableData.value.map(row => row.id)

    if (selection.length > 0) {
      // 全选：添加当前页面所有未选择的主机
      const newSelection = tableData.value.filter(
        row => !selectedHosts.value.some(host => host.id === row.id)
      )
      selectedHosts.value = [...selectedHosts.value, ...newSelection]
    } else {
      // 取消全选：移除当前页面的所有主机
      selectedHosts.value = selectedHosts.value.filter(
        host => !currentPageIds.includes(host.id)
      )
    }
    console.log('selectedHosts', selectedHosts.value)
  }

  /**
   * 显示对话框并初始化选中状态
   */
  async function add(selected) {
    try {
      allGroups.value = await GetAllGroup()
    } catch (err) {
      console.log('获取组失败。。。')
      return false
    }

    // 保存初始选中的主机
    isProgramSelect.value = false
    selectedHosts.value = JSON.parse(JSON.stringify(selected || []))

    // 查询数据
    await handleSearch()

    // 设置选中状态
    setTableSelection()

    visible.value = true
  }

  /**
   * 设置表格选中状态
   */
  function setTableSelection() {
    if (!tableRef.value) return
    
    isProgramSelect.value = true
    // 先清除所有选中状态
    tableData.value.forEach(row => {
      tableRef.value.toggleRowSelection(row, false)
    })

    // 设置选中状态
    tableData.value.forEach(row => {
      if (selectedHosts.value.some(selected => selected.id === row.id)) {
        tableRef.value.toggleRowSelection(row, true)
      }
    })
    isProgramSelect.value = false
  }

  // 监听表格数据变化，重新设置选中状态
  watch(tableData, () => {
    if (visible.value) {
      nextTick(() => {
        setTableSelection()
      })
    }
  })

  defineExpose({add})
</script>

<style scoped>

</style>
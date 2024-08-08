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
                    @selection-change="handleSelectionChange">
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
  // 存储上一次选择的行，可用于对比判定增、删了哪一行
  const prevSelectedRows = ref([])

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
   *
   * @param selection
   */
  function handleSelectionChange(selection) {
    console.log(selectedHosts.value)
    // 找到新增行
    const newSelectedRows = selection.filter((row) => !prevSelectedRows.value.includes(row))
    // 找到取消选择的行
    const deselectedRows = prevSelectedRows.value.filter((row) => !selection.includes(row))
    prevSelectedRows.value = selection
    if (newSelectedRows.length > 0) {
      if (!selectedHosts.value.some(row => row.id === newSelectedRows[0].id)) {
        console.log('add hosts')
        selectedHosts.value.push(newSelectedRows[0])
      }
    }
    if (deselectedRows.length > 0) {
      console.log('deselectedRows')
      selectedHosts.value.forEach((row, index) => {
        if (row.id === deselectedRows[0].id) {
          selectedHosts.value.splice(index, 1)
        }
      })
    }
    console.log(selectedHosts.value)
  }

  /**
   *
   * @param {Array[Object]} selected - 已选择的主机，需要勾选状态
   * @return {Promise<boolean>}
   */
  async function add(selected) {
    try {
      allGroups.value = await GetAllGroup()
    } catch (err) {
      console.log('获取组失败。。。')
      return false
    }
    await handleSearch()
    selectedHosts.value = JSON.parse(JSON.stringify(selected))
    visible.value = true
  }

  watch(tableData, () => {
    // 监听table，更新选中框
    console.log('tableData changed')
    prevSelectedRows.value = []
    console.log(tableData.value)
    // 更新选中的主机
    nextTick(() => {
      console.log('start to nexttick')
      console.log(selectedHosts.value)
      if (selectedHosts.value.length > 0) {
        selectedHosts.value.forEach(item => {
          tableData.value.forEach(data => {
            if (data.id === item.id) {
              console.log(data)
              tableRef.value.toggleRowSelection(data, true)
            }
          })
        })
        prevSelectedRows.value = tableRef.value.getSelectionRows()
        console.log(prevSelectedRows.value)
      }
    })

  })

  defineExpose({add})
</script>

<style scoped>

</style>
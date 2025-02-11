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
  import {ref} from 'vue'
  import {GetAllGroup} from '@/api/host.js'
  import usePagination from '@/composables/usePagination.js'

  const emit = defineEmits(['success'])
  const tableRef = ref(null)
  const visible = ref(false)
  const allGroups = ref([])
  const selectedHosts = ref([])
  const initialSelected = ref([])

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
   * 处理表格选择变化
   */
  function handleSelectionChange(selection) {
    // 如果是初始加载，使用initialSelected的值
    if (initialSelected.value.length > 0) {
      selectedHosts.value = initialSelected.value
      initialSelected.value = []
      return
    }
    selectedHosts.value = selection
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

    // 保存初始选中的主机到两个变量
    initialSelected.value = JSON.parse(JSON.stringify(selected || []))
    selectedHosts.value = JSON.parse(JSON.stringify(selected || []))

    // 查询数据
    await handleSearch()

    console.log(tableData.value)
    // 先清除所有选中状态
    tableData.value.forEach(row => {
      tableRef.value?.toggleRowSelection(row, false)
    })

    console.log('start to selected', selectedHosts.value)
    // 设置选中状态
    selectedHosts.value.forEach(item => {
      console.log(item)
      const found = tableData.value.find(data => data.id === item.id)
      if (found) {
        tableRef.value?.toggleRowSelection(found, true)
      }
    })

    visible.value = true
  }

  defineExpose({add})
</script>

<style scoped>

</style>
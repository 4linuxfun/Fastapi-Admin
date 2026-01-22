<template>
  <el-row style="height: 100%" :gutter="20">
    <!--    左侧分组列表-->
    <el-col :span="6" style="height: 100%">
      <div class="col-style">
        <span style="padding: 10px">分组列表</span>
        <el-button type="primary" @click="handleAddChild">新建分组</el-button>
        <el-divider style="margin-bottom: 0"/>
        <div style="height: 90%;overflow-y: scroll;">
          <el-tree ref="elTreeRef" :data="treeData" :props="{label:'name'}"
                   style="padding: 10px" highlight-current default-expand-all
                   :expand-on-click-node="false">
            <template #default="{node,data}">
              <el-row style="flex: 1" justify="space-between">
                <el-col :span="18" @click="handleSearchHost(data)"><span>{{ node.label }}</span></el-col>
                <el-col :span="6" style="text-align: right">
                  <el-link underline="never" style="margin-left: 10px" @click="handleEditGroup(data)">
                    <el-icon>
                      <Edit/>
                    </el-icon>
                  </el-link>
                  <el-link underline="never" style="margin-left: 10px" @click="handleDelGroup(data.id)">
                    <el-icon color="red">
                      <Delete/>
                    </el-icon>
                  </el-link>
                </el-col>
              </el-row>
            </template>
          </el-tree>
        </div>
      </div>
    </el-col>
    <!--    右侧主机列表-->
    <el-col :span="18">
      <div class="col-style">
        <el-row justify='space-between'>
          <el-col :span="12">
            <el-row :gutter="5">
              <el-col :span="10">
                <el-input v-model="search.name" @keyup.enter="handleSearch" clearable placeholder="输入名称"/>
              </el-col>
              <el-col :span="10">
                <el-input v-model="search.ansible_host" @keyup.enter="handleSearch" clearable placeholder="输入主机IP"/>
              </el-col>
              <el-col :span="2">
                <el-button type="primary" @click="handleSearch">搜索</el-button>
              </el-col>
            </el-row>
          </el-col>
          <el-col :span="8">
            <el-button type="primary" @click="hostDialogRef.add()">新建</el-button>
            <el-button type="primary" @click="PingHost(5)">验证</el-button>
            <el-button>全部</el-button>
            <el-button>未验证</el-button>
          </el-col>
        </el-row>
        <el-table :data="tableData" border style="margin-top: 10px">
          <el-table-column type="index" label="#" align="center"/>
          <el-table-column prop="name" label="主机名" align="center"/>
          <el-table-column prop="ansible_host" label="主机IP" align="center"/>
          <el-table-column prop="ansible_port" label="主机端口" align="center"/>
          <el-table-column prop="desc" label="描述" align="center"/>
          <el-table-column label="配置" align="center">
            <template #default="scope">
              <el-button text :icon="Edit" type="primary" @click="handleEditHost(scope.row.id)">编辑</el-button>
              <el-popconfirm title="确定删除主机吗？" @confirm="handleDelHost(scope.row.id)">
                <template #reference>
                  <el-button text :icon="Delete" type="danger">删除</el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total" background
                       layout="total,prev,pager,next,sizes,jumper"
                       style="margin-top: 10px;"
        />
      </div>
    </el-col>
  </el-row>


  <add-group ref="addGroupRef" @close="handleFreshAll"/>
  <host-dialog ref="hostDialogRef" @close="freshCurrentPage"/>

</template>

<script setup>
  defineOptions({
    name: '主机管理'
  })

  import {ref, onMounted} from 'vue'
  import {Delete, Edit} from '@element-plus/icons-vue'
  import {GetAllGroup, DelHost, DelGroup, PingHost} from '@/api/host.js'
  import HostDialog from '@/views/host/HostDialog.vue'
  import usePagination from '@/composables/usePagination.js'
  import AddGroup from '@/views/host/AddGroup.vue'
  import {ConfirmDel} from '@/utils/request.js'

  const treeData = ref([])
  const elTreeRef = ref(null)
  const addGroupRef = ref(null)
  const hostDialogRef = ref(null)
  const selectTreeNodeData = ref(null)

  const searchForm = {
    name: null,
    ansible_host: null,
    group_id: null,
    ancestors: null
  }

  // 首次打开页面先进行初始化

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


  /**
   * 添加分组
   */
  async function handleAddChild() {
    await addGroupRef.value.add()
  }

  /**
   * 编辑分组
   * @param data
   * @return {Promise<void>}
   */
  async function handleEditGroup(data) {
    console.log(data)
    await addGroupRef.value.edit(data)
  }

  function handleSearchHost(groupInfo) {
    console.log('点击')
    console.log(groupInfo)
    search.group_id = groupInfo.id
    search.ancestors = groupInfo.ancestors
    handleSearch()
  }


  async function handleFreshGroups() {
    try {
      treeData.value = await GetAllGroup()
    } catch (e) {
      console.log(e)
    }
  }

  /**
   * 刷新group和host列表
   * */
  function handleFreshAll() {
    handleFreshGroups()
    freshCurrentPage()
  }

  function handleEditHost(hostId) {
    hostDialogRef.value.edit(hostId)
  }

  async function handleDelHost(hostId) {
    try {
      await DelHost(hostId)
    } catch (err) {
      console.log(err)
    }
    freshCurrentPage()
  }

  async function handleDelGroup(groupId) {
    try {
      await ConfirmDel('删除分组', DelGroup, groupId)
    } catch (e) {
      console.log(e)
    }
    await handleFreshGroups()
  }

  onMounted(() => {
    GetAllGroup().then((data) => {
      treeData.value = data
    })
    handleSearch()
  })
</script>

<style scoped>
.col-style {
  height: calc(100% - 40px);
  background-color: rgb(255, 255, 255);
  padding: 20px;
}

.el-tree--highlight-current .el-tree-node.is-current > :deep(.el-tree-node__content) {
  background-color: #79bbff;
}
</style>
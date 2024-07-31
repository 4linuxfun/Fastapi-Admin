<template>
  <el-row style="height: 100%" :gutter="20">
    <!--    左侧分组列表-->
    <el-col :span="6" style="height: 100%">
      <div class="col-style">
        <span style="padding: 10px">分组列表</span>
        <el-button type="primary" @click="addRootDialog=true">新建根分组</el-button>
        <el-divider style="margin-bottom: 0"/>
        <div style="height: 90%;overflow-y: scroll;">
          <el-tree ref="elTreeRef" :data="treeData" :props="{label:'name'}"
                   style="padding: 10px" highlight-current default-expand-all
                   :expand-on-click-node="false"
                   @node-drop="handleDrop"
                   @node-contextmenu="handleContextMenu">
            <template #default="{node,data}">
              <el-row style="flex: 1" justify="space-between" @click="handleSearchHost(data.id)">
                <el-col :span="6"><span>{{ node.label }}</span></el-col>
                <el-col :span="6" style="text-align: right">
                  <el-link v-if="data.hasOwnProperty('children')" :underline="false" @click="handleAddChild(data.id)">
                    <el-icon>
                      <Plus/>
                    </el-icon>
                  </el-link>
                  <el-link :underline="false" style="margin-left: 10px">
                    <el-icon>
                      <Edit/>
                    </el-icon>
                  </el-link>
                  <el-link :underline="false" style="margin-left: 10px" @click="handleDelGroup(data.id)">
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

  <el-dialog v-model="addRootDialog" width="500px" title="新增分组" destroy-on-close
             @close="handleFreshGroups">
    <el-form ref="addRootFormRef" :model="addRootForm">
      <el-form-item label="分组名：" prop="name" :rules="[{required:true,message:'请输入分组名'}]">
        <el-input v-model="addRootForm.name"/>
      </el-form-item>
    </el-form>
    <el-row justify="end">
      <el-button type="primary" @click="handleAddRoot">提交</el-button>
      <el-button type="danger" @click="addRootDialog=false">取消</el-button>
    </el-row>
  </el-dialog>

  <host-dialog ref="hostDialogRef" @close="freshCurrentPage"/>

</template>

<script setup>
  import {ref, reactive, onMounted} from 'vue'
  import {Contextmenu, ContextmenuItem} from 'v-contextmenu'
  import {Close, Delete, DocumentAdd, Edit, Folder, FolderAdd, Switch} from '@element-plus/icons-vue'
  import {PostNewGroup, GetAllGroup, DelHost, DelGroup, PingHost} from '@/api/host.js'
  import HostDialog from '@/views/host/HostDialog.vue'
  import usePagination from '@/composables/usePagination.js'

  const treeData = ref([])
  const elTreeRef = ref(null)
  const addRootFormRef = ref(null)
  const hostDialogRef = ref(null)
  const inputRef = ref(null)
  const selectTreeNodeData = ref(null)
  const editTreeNodeId = ref(null)
  const newNodeName = ref(null)
  const addRootDialog = ref(false)
  const addRootForm = reactive({name: null, parent_id: null})
  const searchForm = {
    name: null,
    ansible_host: null,
    group_id: null
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


  function handleDrop() {
    console.log('end drag')
  }

  /**
   * el-tree右键菜单处理
   */
  function handleContextMenu(e, data, node,) {
    console.log('右键菜单', e, data, node)
    selectTreeNodeData.value = node
  }

  function showContextMenu(node) {
    console.log('显示右键菜单', node)
  }

  /**
   * 添加子分组
   */
  function handleAddChild(parentId) {
    Object.assign(addRootForm, {name: null, parent_id: parentId})
    addRootDialog.value = true
  }

  function handleSearchHost(groupId) {
    console.log('点击')
    console.log(groupId)
    search.group_id = groupId
    handleSearch()
  }

  /**
   * 添加根分组的函数
   */
  async function handleAddRoot() {
    console.log('添加根分组')
    // treeData.value.push({label: '', children: []})
    try {
      await addRootFormRef.value.validate()
      console.log('submit')
      await PostNewGroup(addRootForm)
      addRootDialog.value = false
    } catch (err) {
      console.log('error submit', err)
    }
  }

  function handleFreshGroups() {
    Object.assign(addRootForm, {name: null, parent_id: null})
    GetAllGroup().then((data) => {
      treeData.value = data
    })
  }

  function handleEdit(node, data) {
    console.log('双击编辑事件', node, data)
    editTreeNodeId.value = node.id
    newNodeName.value = data.label
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

  function handleUpdateNodeName(node, data) {
    console.log(node)
    if (data.hasOwnProperty('id')) {
      console.log('更新节点信息')
    } else {
      console.log('新增节点信息')
      console.log('parentID:', node.parent.id)
      data.label = newNodeName.value
      PostNewGroup({name: newNodeName.value, parent_id: node.parent.id})
      // data.id = data.$treeNodeId
      editTreeNodeId.value = null
      newNodeName.value = null

    }
    console.log(treeData.value)

    // PostNewGroup({name:data.label,parent_id:})
  }

  async function handleDelGroup(groupId) {
    console.log('删除节点：' + groupId)
    try {
      await DelGroup(groupId)
    } catch (err) {
      console.log(err)
    }
    handleFreshGroups()
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
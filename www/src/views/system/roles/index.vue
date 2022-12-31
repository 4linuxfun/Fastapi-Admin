<template>
  <el-row>
    <el-form :model="search" inline ref="searchRef">
      <el-form-item label="角色名称" prop="name">
        <el-input v-model="search.name"/>
      </el-form-item>
      <el-form-item label="状态" prop="enable">
        <auto-dict dict-type="select" code="enable_code" v-model="search.enable" style="width: 100px"/>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSearch" :icon="Search">
          搜索
        </el-button>
        <el-button type="primary" @click="handleReset" :icon="RefreshRight">重置</el-button>
        <el-button v-permission="'role:add'" type="primary" @click="addRole" :icon="Plus">添加新角色</el-button>
      </el-form-item>
    </el-form>
  </el-row>

  <div style="padding-top:10px">
    <el-table :data="tableData" border stripe :header-cell-style="{background:'#eef1f6',color:'#606266'}">
      <el-table-column label="#" type="index"></el-table-column>
      <el-table-column label="角色名称" prop="name"></el-table-column>
      <el-table-column label="描述" prop="description"></el-table-column>
      <el-table-column label="状态">
        <template #default="scope">
          <el-tag effect="dark" :type="scope.row.enable === true?'success':'danger'">
            {{ scope.row.enable === true ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作">
        <template #default="scope">
          <el-button v-permission="'role:update'" v-if="scope.row.name!='admin'" type="primary" size="small"
                     @click="handleEdit(scope.row)">编辑
          </el-button>
          <el-button v-permission="'role:del'" v-if="scope.row.name!='admin'" type="danger" size="small"
                     @click="handleDel(scope.row)">删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
  <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total" background
                 layout="total,prev,pager,next,sizes,jumper"
                 style="margin-top: 10px;"
  />

  <div v-if="dialogVisible">
    <role-dialog :role='selectRole' v-model:visible='dialogVisible'></role-dialog>
  </div>

</template>
<script setup>
  import {reactive, ref, watch} from 'vue'
  import {Search, RefreshRight, Plus} from '@element-plus/icons-vue'
  import {GetRoles, DeleteRole} from '@/api/roles'
  import usePagination from '@/composables/usePagination'
  import RoleDialog from './RoleDialog.vue'
  import {ElMessageBox, ElNotification} from 'element-plus'
  import AutoDict from '@/components/AutoDict'

  const dialogVisible = ref(false)
  const selectRole = reactive({})
  const addDialog = ref(false)
  const searchRef = ref(null)
  const selectOptions = ref(null)

  const searchForm = {
    name: null,
    enable: null
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
  } = usePagination('/api/roles/search', searchForm)


  watch(dialogVisible, (newValue) => {
    if (newValue === false) {
      freshCurrentPage()
    }
  })

  function handleReset() {
    searchRef.value.resetFields()
    handleSearch()
  }

  function handleEdit(role) {
    console.log(role)
    Object.assign(selectRole, role)
    console.log(selectRole)
    dialogVisible.value = true
  }

  function handleDel(role) {
    ElMessageBox.confirm('是否确定要删除角色：' + role.name, 'Warnning', {type: 'warning'}).then(() => {
      DeleteRole(role.id).then(() => {
        ElNotification({
          title: 'success',
          message: '角色删除成功',
          type: 'success'
        })
        freshCurrentPage()
      })
    }).catch(() => {
      ElNotification({
        title: 'success',
        message: '取消删除操作',
        type: 'success'
      })
    })

  }

  function addRole() {
    Object.assign(selectRole, {
      id: null,
      name: '',
      description: '',
      enable: true
    })
    console.log(selectRole)
    dialogVisible.value = true
  }

</script>
<style lang="">

</style>
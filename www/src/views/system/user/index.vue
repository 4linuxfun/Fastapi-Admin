<template>
  <el-row style="width:300px" :gutter="5">
    <el-col :span="18">
      <el-input v-model="search" placeholder="搜索" clearable>
        <template #append>
          <el-button @click="handleSearch">
            <el-icon>
              <Search/>
            </el-icon>
          </el-button>
        </template>
      </el-input>
    </el-col>
    <el-col :span="6">
      <el-button v-permission="'user:add'" type="primary" @click="handleAdd">添加新用户</el-button>
    </el-col>
  </el-row>

  <div style="padding-top:10px">
    <el-table :data="tableData" border style="width: 100%" stripe
              :header-cell-style="{background:'#eef1f6',color:'#606266'}">
      <el-table-column label="#" type="index" width="50"/>
      <el-table-column prop="name" label="用户名" align="center"/>
      <el-table-column prop="email" label="邮箱" align="center"/>
      <el-table-column prop="avatar" label="头像" align="center"/>
      <el-table-column label="状态" align="center">
        <template #default="scope">
          <el-tag effect="dark" :type="scope.row.enable === true?'success':'danger'">
            {{ scope.row.enable === true ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center">
        <template #default="scope">
          <el-dropdown @command="handleCommand">
            <span style="color: deepskyblue">
              更多<el-icon>
              <arrow-down/>
            </el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item :command="beforeHandleCommand(scope.row,'detail')">详情</el-dropdown-item>
                <el-dropdown-item :command="beforeHandleCommand(scope.row,'password')">密码</el-dropdown-item>
                <el-dropdown-item :command="beforeHandleCommand(scope.row,'delete')">删除</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <!--          <el-button type="primary" size="small" @click="handleEdit(scope.row.id)">编辑</el-button>-->
          <!--          <el-button type="danger" size="small" @click="handleDel(scope.row)">删除</el-button>-->
        </template>
      </el-table-column>
    </el-table>
    <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total" background
                   layout="total,prev,pager,next,sizes,jumper"
                   style="margin-top: 10px;"
    />

  </div>
  <el-dialog v-model="resetPasswdDialog" title="用户密码重置" width="30%" @close="resetPasswdDialog=false">
    <change-passwd :user='selectUser' v-model:visible="resetPasswdDialog"/>
  </el-dialog>

  <el-drawer v-model="detailVisible" title="用户详情" destroy-on-close>
    <user-dialog :user='selectUser' v-model:visible='detailVisible'/>
  </el-drawer>

</template>
<script setup>
  import {
    reactive,
    ref, watch
  } from 'vue'
  import {
    ArrowDown,
    Search
  } from '@element-plus/icons-vue'
  import UserDialog from './UserDialog.vue'
  import ChangePasswd from './ChangePasswd'
  import usePagination from '@/composables/usePagination'
  import {
    PutNewUser,
    PostAddUser,
    DeleteUser, GetUserInfo
  } from '@/api/users'
  import {ElMessage, ElMessageBox, ElNotification, ElPopconfirm} from 'element-plus'


  const formData = reactive({})
  const formSchema = reactive({})
  const dialogVisible = ref(false)
  const detailVisible = ref(false)
  const resetPasswdDialog = ref(false)
  const selectUser = reactive({})

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
  } = usePagination('/api/users/search')

  function handleChangePwd(user) {
    resetPasswdDialog.value = true
    Object.assign(selectUser, user)
  }

  function beforeHandleCommand(row, command) {
    return {
      row,
      command
    }
  }

  function handleCommand(command) {
    switch (command.command) {
      case 'detail':
        handleEdit(command.row.id)
        break
      case 'password':
        handleChangePwd(command.row)
        break
      case 'delete':
        handleDel(command.row)
        break
    }
  }

  function handleEdit(uid) {
    console.log(uid)
    GetUserInfo(uid).then(response => {
      Object.assign(selectUser, response)
      detailVisible.value = true
    })
    console.log(selectUser)
  }

  function handleAdd() {
    console.log('start to add user')
    Object.assign(selectUser, {
      id: null,
      name: null,
      email: '',
      enable: 0,
      avatar: '',
      password: null,
    })
    console.log(selectUser)
    detailVisible.value = true
  }

  function handleSubmit() {
    console.log(formData)
    dialogVisible.value = false
  }

  function handleDel(userInfo) {
    if (userInfo.name === 'admin') {
      ElMessage({
        message: 'admin用户无法删除',
        type: 'warning'
      })
      return false
    }
    ElMessageBox.confirm('是否确定要删除用户：' + userInfo.name, '警告', {type: 'warning'}).then(() => {
      DeleteUser(userInfo.id).then(() => {
        ElMessage({
          title: 'success',
          message: userInfo.name + '用户删除成功',
          type: 'success'
        })
        freshCurrentPage()
      })
    }).catch(() => {
      ElMessage({
        title: 'success',
        message: '取消删除操作',
        type: 'warning'
      })
    })
  }

  watch(
      detailVisible, (newValue, oldValue) => {
        freshCurrentPage()
      })

</script>

<style>
</style>

<template>
  <el-row style="width:300px" :gutter="5">
    <el-col :span="18">
      <el-input v-model="search" placeholder="搜索" clearable>
        <template #append>
          <el-button @click="handleSearch">
            <el-icon>
              <search/>
            </el-icon>
          </el-button>
        </template>
      </el-input>
    </el-col>
    <el-col :span="6">
      <el-button type="primary" @click="handleAdd">添加新用户</el-button>
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
          <el-tag effect="dark" :type="scope.row.enable === 1?'success':'danger'">
            {{ scope.row.enable === 1 ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center">
        <template #default="scope">
          <el-button type="primary" size="small" @click="handleEdit(scope.row.id)">编辑</el-button>
          <el-button type="danger" size="small" @click="handleDel(scope.row.id,scope.row.name)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total" background
                   layout="prev,pager,next"
                   prev-text="上一页" next-text="下一页"
    />

  </div>
  <user-dialog :user='selectUser' v-model:visible='dialogVisible'/>

</template>
<script>
  import {
    reactive,
    ref
  } from 'vue'
  import {
    Search
  } from '@element-plus/icons-vue'
  import UserDialog from './UserDialog.vue'
  import usePagination from '@/composables/usePagination'
  import {
    PutNewUser,
    PostAddUser,
    DeleteUser, GetUserInfo
  } from '@/api/users'


  export default {
    name: 'UserPage',
    components: {
      Search,
      'user-dialog': UserDialog,
      // 'auto-form-dialog': AutoFormDialog
    },
    setup() {
      const formData = reactive({})
      const formSchema = reactive({})
      const dialogVisible = ref(false)
      const selectUser = reactive({})

      // 首次打开页面先进行初始化

      const {
        search,
        tableData,
        currentPage,
        pageSize,
        total,
        firstId,
        lastId,
        freshCurrentPage,
        handleSearch
      } = usePagination('/api/users')
      return {
        formData,
        formSchema,
        search,
        dialogVisible,
        tableData,
        selectUser,
        pageSize,
        currentPage,
        total,
        lastId,
        firstId,
        freshCurrentPage,
        handleSearch
      }
    },
    methods: {

      handleEdit(uid) {
        console.log(uid)
        this.dialogVisible = true
        GetUserInfo(uid).then(response => {
          this.selectUser = response
        })

        console.log(this.selectUser)
      },

      handleAdd() {
        console.log('start to add user')
        this.dialogVisible = true
        this.selectUser = {
          name: '',
          email: '',
          enable: 0,
          avatar: '',
        }
        console.log(this.selectUser)

      },
      handleSubmit() {
        console.log(this.formData)
        this.dialogVisible = false
      },
      handleDel(userId, userName) {
        if (userName === 'admin') {
          this.$message({
            message: 'admin用户无法删除',
            type: 'warning'
          })
          return false
        }
        this.$confirm('是否确定要删除用户：' + userName, 'Warnning').then(() => {
          DeleteUser(userId).then(() => {
            this.$notify({
              title: 'success',
              message: '角色删除成功',
              type: 'success'
            })
            this.freshCurrentPage()
          })
        }).catch(() => {
          this.$notify({
            title: 'success',
            message: '取消删除操作',
            type: 'success'
          })
        })
      }
    },
  }
</script>

<style>
</style>

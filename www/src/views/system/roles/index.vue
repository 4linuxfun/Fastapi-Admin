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
      <el-button v-permission="'addRole'" type="primary" @click="addRole">添加新角色</el-button>
    </el-col>
  </el-row>

  <div style="padding-top:10px">
    <el-table :data="tableData" border stripe :header-cell-style="{background:'#eef1f6',color:'#606266'}">
      <el-table-column label="角色ID" prop="id"></el-table-column>
      <el-table-column label="角色名称" prop="name"></el-table-column>
      <el-table-column label="描述" prop="description"></el-table-column>
      <el-table-column label="状态">
        <template #default="scope">
          <el-tag effect="dark" :type="scope.row.enable === 1?'success':'danger'">
            {{ scope.row.enable === 1 ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作">
        <template #default="scope">
          <el-button v-permission="'editRole'" v-if="scope.row.name!='admin'" type="primary" size="small"
                     @click="handleEdit(scope.row)">编辑
          </el-button>
          <el-button v-permission="'delRole'" v-if="scope.row.name!='admin'" type="danger" size="small"
                     @click="handleDel(scope.row)">删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
  <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total" background
                 layout="prev,pager,next"
                 prev-text="上一页" next-text="下一页"
  />

  <div v-if="dialogVisible">
    <role-dialog :role='selectRole' v-model:visible='dialogVisible'></role-dialog>
  </div>

</template>
<script>
  import {ref} from 'vue'
  import {Search} from '@element-plus/icons-vue'
  import {GetRoles, DeleteRole} from '@/api/roles'
  import usePagination from '@/composables/usePagination'
  import RoleDialog from './RoleDialog.vue'

  export default {
    name: 'RoleView',
    components: {
      Search,
      'role-dialog': RoleDialog
    },
    setup() {
      const dialogVisible = ref(false)
      const selectRole = ref(null)
      const addDialog = ref(false)

      const {
        search,
        tableData,
        currentPage,
        pageSize,
        orderModel,
        total,
        freshCurrentPage,
        handleSearch
      } = usePagination('/api/roles/search')

      console.log(tableData.value)
      return {
        dialogVisible,
        selectRole,
        addDialog,
        search,
        tableData,
        currentPage,
        pageSize,
        orderModel,
        total,
        freshCurrentPage,
        handleSearch
      }
    },

    watch: {
      dialogVisible(newValue) {
        if (newValue === false) {
          this.freshCurrentPage()
        }
      },
    },
    methods: {
      handleEdit(role) {
        console.log(role)
        this.selectRole = Object.assign({}, role)
        console.log(this.selectRole)
        this.dialogVisible = true
      },

      handleDel(role) {
        this.$confirm('是否确定要删除角色：' + role.name, 'Warnning').then(() => {
          DeleteRole(role.id).then(() => {
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

      },
      addRole() {
        this.selectRole = {
          id: null,
          name: '',
          description: '',
          enable: ''
        }
        console.log(this.selectRole)
        this.dialogVisible = true
      }
    },

  }
</script>
<style lang="">

</style>
// 菜单管理页面，用于创建菜单关系：菜单名、菜单页面、二级菜单。。。等等
<template>
  <el-row style="width:300px" :gutter="5">
    <el-col :span="18">
      <el-input v-model="search" placeholder="搜索" clearable>
        <template #append>
          <el-button @click="getMenuInfo">
            <el-icon>
              <search/>
            </el-icon>
          </el-button>
        </template>
      </el-input>
    </el-col>
    <el-col :span="6">
      <el-button type="primary" @click="handleAdd">新增</el-button>
    </el-col>
  </el-row>
  <div style="padding-top:10px">
    <el-table :data="menuData" style="width: 100%; margin-bottom: 20px;" row-key="id" border stripe
              :header-cell-style="{background:'#eef1f6',color:'#606266'}">
      <!--      <el-table-column prop="id" label="主键" width="180"/>-->
      <el-table-column prop="name" label="名称" width="180"/>
      <el-table-column prop="type" label="类型" width="100" align="center">
        <template #default="scope">
          <el-tag effect="dark" v-if="scope.row.type === 'page'" type='info'>
            一级菜单
          </el-tag>
          <el-tag effect="dark" v-else-if="scope.row.type === 'subPage'" type='success'>
            子菜单
          </el-tag>
          <el-tag effect="dark" v-else type="warning">按钮</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="path" label="路径" width="180"/>
      <el-table-column prop="component" label="组件" width="180"/>
      <el-table-column prop="apis" label="关联API权限" align="center">
        <template #default="scope">
          <el-tag v-for="api in scope.row.apis" type='info' :key="api.id">{{ api.tags }}-{{ api.summary }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="enable" label="状态" width="80">
        <template #default="scope">
          <el-tag effect="dark" :type="scope.row.enable === 1?'success':'danger'">
            {{ scope.row.enable === 1 ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作">
        <template #default="scope">
          <el-dropdown @command="handleCommand">
            <span style="color: deepskyblue">
              更多<el-icon>
              <arrow-down/>
            </el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item :command="beforeHandleCommand(scope.row,'detail')">编辑</el-dropdown-item>
                <el-dropdown-item :command="beforeHandleCommand(scope.row,'password')">添加子菜单</el-dropdown-item>
                <el-dropdown-item :command="beforeHandleCommand(scope.row,'delete')">删除</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
      </el-table-column>
      >
    </el-table>

  </div>
  <el-drawer v-model="dialogVisible" title="添加子菜单" destroy-on-close>
    <menu-dialog :data="selectData" v-model:visible="dialogVisible"></menu-dialog>
  </el-drawer>

</template>
<script>
  import {Search, ArrowDown} from '@element-plus/icons-vue'
  import {ElMessageBox} from 'element-plus'
  import {
    DeleteMenu,
    GetAllMenus
  } from '@/api/menus'
  import MenuDialog from './MenuDialog'
  import {provide, reactive, ref, watch} from 'vue'

  export default {
    components: {
      ArrowDown,
      Search,
      'menu-dialog': MenuDialog,
    },
    setup() {
      const search = ref(null)
      const dialogVisible = ref(false)
      const menuInfo = reactive({
        name: '',
        status: ''
      })
      const menuData = ref([])
      const selectData = reactive({})

      provide('menuData', menuData)

      watch(dialogVisible, (newValue) => {
        if (newValue === false) {
          getMenuInfo()
        }
      })

      const beforeHandleCommand = (row, command) => {
        return {
          row,
          command
        }
      }
      const handleCommand = (command) => {
        let row = command.row
        switch (command.command) {
          case 'detail':
            dialogVisible.value = true
            Object.assign(selectData, row)
            break
          case 'password':
            this.handleChangePwd(command.row)
            break
          case 'delete':
            ElMessageBox.confirm('是否删除菜单：' +row.name, '删除菜单', {
              type: 'warning'
            }).then(() => {
              DeleteMenu(row.id)
              getMenuInfo()
            }).catch()
            break
        }
      }

      const splitApis = (apis) => {
        console.log('split')
        console.log(apis)
        return apis.split(',')
      }

      const onSubmit = () => {
        console.log('submit!')
      }


      const handleDelete = (id, name) => {

      }

      const handleAdd = () => {
        Object.assign(selectData, {
          id: null,
          parent_id: null,
          name: '',
          path: '',
          component: null,
          enable: '',
          type: 'page'
        })
        dialogVisible.value = true
      }

      const getMenuInfo = () => {
        console.log('get menu info')
        GetAllMenus(search.value).then(response => {
          console.log(response)
          menuData.value = response
        }).catch(error => {
          this.$notify({
            title: '错误',
            message: error,
            type: 'error'
          })
        })
      }

      return {
        search,
        dialogVisible,
        menuInfo,
        // 表格数据
        menuData,
        // 点击编辑菜单时选择的数据
        selectData,
        beforeHandleCommand,
        handleCommand,
        splitApis,
        onSubmit,
        handleDelete,
        handleAdd,
        getMenuInfo
      }

    },
    created() {
      console.log('start to get all menu list')
      this.getMenuInfo()
    }
  }
</script>
<style lang="">

</style>

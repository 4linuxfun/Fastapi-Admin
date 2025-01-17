// 菜单管理页面，用于创建菜单关系：菜单名、菜单页面、二级菜单。。。等等
<template>
  <el-row>
    <el-button v-permission="'menu:add'" type="primary" @click="handleAdd()" :icon="Plus">新建菜单</el-button>
  </el-row>

  <div style="padding-top:10px">
    <el-table :data="menuData"
              style="width: 100%; margin-bottom: 20px;" row-key="id" border stripe
              :header-cell-style="{background:'#eef1f6',color:'#606266'}">
      <!--      <el-table-column prop="id" label="主键" width="180"/>-->
      <el-table-column prop="name" label="菜单名称" width="180" align="left" header-align="center"/>
      <el-table-column prop="type" label="菜单类型" width="100" align="center">
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
      <el-table-column prop="icon" label="图标" width="100" align="center">
        <template #default="scope">
          <el-icon v-if="scope.row.icon">
            <component :is="scope.row.icon"/>
          </el-icon>
        </template>
      </el-table-column>
      <el-table-column prop="path" label="路径" width="180" align="center"/>
      <el-table-column prop="component" label="组件" width="180" align="center"/>
      <el-table-column prop="sort" label="排序" align="center"/>
      <el-table-column prop="enable" label="状态" width="80" align="center">
        <template #default="scope">
          <el-tag effect="dark" :type="scope.row.enable === true?'success':'danger'">
            {{ scope.row.enable === true ? '启用' : '禁用' }}
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
                <el-dropdown-item :command="beforeHandleCommand(scope.row,'detail')">编辑
                </el-dropdown-item>
                <el-dropdown-item v-if="scope.row.type === 'page'"
                                  :command="beforeHandleCommand(scope.row,'addSubPage')">添加子菜单
                </el-dropdown-item>
                <el-dropdown-item :command="beforeHandleCommand(scope.row,'delete')">删除
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
      </el-table-column>
    </el-table>

  </div>
  <menu-drawer ref="menuDrawerRef" @success="getMenuInfo"/>

</template>


<script setup>
  import {Plus, ArrowDown} from '@element-plus/icons-vue'
  import {ElMessageBox} from 'element-plus'
  import {
    DeleteMenu,
    GetAllMenus
  } from '@/api/menus'
  import {provide, reactive, ref, shallowRef, watch} from 'vue'
  import MenuDrawer from '@/views/system/menus/MenuDrawer.vue'

  defineOptions({
    name: '菜单管理'
  })

  const dialogVisible = ref(false)
  const menuInfo = reactive({
    name: '',
    status: ''
  })
  const menuData = shallowRef([])
  const selectData = reactive({})
  const menuDrawerRef = ref(null)

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
        menuDrawerRef.value.edit(row)
        break
      case 'addSubPage':
        handleAdd(row.id, 'subPage')
        break
      case 'delete':
        ElMessageBox.confirm('是否删除菜单：' + row.name, '删除菜单', {
          type: 'warning'
        }).then(() => {
          DeleteMenu(row.id)
          getMenuInfo()
        }).catch()
        break
    }
  }

  const handleAdd = (parentId = null, menuType = 'page') => {
    menuDrawerRef.value.add(parentId, menuType)
  }

  const getMenuInfo = () => {
    console.log('get menu info')
    GetAllMenus().then(response => {
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
  getMenuInfo()
</script>
<style lang="">

</style>

<template>
  <el-dialog :model-value="visible" title="角色编辑页面" width="50%" @close="$emit('update:visible', false)"
             @opened="GetInfo" destroy-on-close>
    <el-form :model="selectData" label-width="80px">
      <el-form-item label="角色名称">
        <el-input v-model="selectData.name"></el-input>
      </el-form-item>
      <el-form-item label="角色描述">
        <el-input v-model="selectData.description"></el-input>
      </el-form-item>
      <el-form-item label="状态">
        <el-radio-group v-model="selectData.enable">
          <el-radio :label="0">禁用</el-radio>
          <el-radio :label="1">启用</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="菜单权限" style="border-style: solid;">
        <el-tree ref="menuTree" :data="menus" :props="defaultProps" show-checkbox node-key="id"
                 :default-checked-keys="enables"></el-tree>
      </el-form-item>
      <el-form-item>
        <el-button @click="$emit('update:visible', false)">取消</el-button>
        <el-button v-if="selectData.id" type="primary" @click="handleUpdate">更新</el-button>
        <el-button v-else type="primary" @click="handleUpdate">添加</el-button>
      </el-form-item>
    </el-form>
  </el-dialog>
</template>

<script>
  import {ref, reactive} from 'vue'
  import {
    GetRoleEnableMenus,
    PutRoles,
    PostNewRoles,
  } from '@/api/roles'
  import {ElNotification} from 'element-plus'

  export default {
    props: ['role', 'visible'],
    emits: ['update:visible'],
    setup(props, {
      emit
    }) {
      const selectData = reactive(props.role)
      const menus = ref([])
      const defaultProps = reactive({
        children: 'children',
        label: 'name'
      })
      const enables = ref([])
      const category = ref([])
      const categoryEnables = ref([])

      //tree的用法
      const menuTree = ref(null)

      const GetInfo = () => {
        console.log('id:' + selectData.id)
        GetRoleEnableMenus(selectData.id).then((response) => {
          console.log(response)
          menus.value = response.menus
          enables.value = response.enable
        })
      }

      const handleUpdate = () => {
        let checkedKeys = menuTree.value.getCheckedKeys().concat(menuTree.value.getHalfCheckedKeys())
        console.log(checkedKeys)
        selectData.menus = checkedKeys
        console.log(selectData)
        if (selectData.id === null) {
          PostNewRoles(selectData).then(() => {
            ElNotification({
              title: 'success',
              message: '角色新建成功',
              type: 'success'
            })
          }).catch((error) => {
            ElNotification({
              title: 'error',
              message: '角色新建失败：' + error,
              type: 'error'
            })
          })
        } else {
          PutRoles(selectData).then(() => {
            console.log('notification')
            ElNotification({
              title: 'success',
              message: '角色更新成功',
              type: 'success'
            })
          }).catch((error) => {
            ElNotification({
              title: 'error',
              message: '失败：' + error,
              type: 'error'
            })
          })
        }

        emit('update:visible', false)
      }

      GetInfo()
      console.log(enables.value)
      return {
        menuTree,
        selectData,
        menus,
        defaultProps,
        enables,
        category,
        categoryEnables,
        GetInfo,
        handleUpdate
      }
    },
  }
</script>

<style>
</style>

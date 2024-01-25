<template>
  <el-dialog v-model="visible" title="角色编辑页面" width="50%" @close="visible=false"
             destroy-on-close>
    <el-form :model="selectData" label-width="80px" :rules="rules">
      <el-form-item label="角色名称" prop="name">
        <el-input v-model="selectData.name"></el-input>
      </el-form-item>
      <el-form-item label="角色描述">
        <el-input v-model="selectData.description"></el-input>
      </el-form-item>
      <el-form-item label="状态">
        <auto-dict v-model="selectData.enable" dict-type="switch" code="enable_code"/>
      </el-form-item>
      <el-form-item label="菜单权限">
        <el-tree ref="menuTree" :data="menus" :props="defaultProps" accordion show-checkbox node-key="id"
                 :default-checked-keys="enables" check-strictly>
          <template #default="{data}">
            <el-icon v-if="data.icon">
              <component :is="data.icon"/>
            </el-icon>
            <span>{{ data.name }}</span>
          </template>
        </el-tree>
      </el-form-item>
      <el-form-item>
        <el-button type="danger" @click="visible=false">取消</el-button>
        <el-button type="primary" @click="handleUpdate">确定</el-button>
      </el-form-item>
    </el-form>
  </el-dialog>
</template>

<script setup>
  import {ref, reactive, onMounted} from 'vue'
  import {
    GetRoleEnableMenus,
    PutRoles,
    PostNewRoles, GetRoleExist,
  } from '@/api/roles'
  import {ElNotification} from 'element-plus'
  import AutoDict from '@/components/AutoDict'

  const emit = defineEmits(['success'])
  const visible = ref(false)
  const selectData = reactive({})
  const menus = ref([])
  const defaultProps = reactive({
    children: 'children',
    label: 'name',
    class: customNodeClass
  })
  const enables = ref([])

  //tree的用法
  const menuTree = ref(null)

  const rules = reactive({
    name: [{required: true, trigger: 'blur', message: '请输入角色名'},
      {
        required: true, trigger: 'blur',
        validator: (rule, value, callback) => {
          GetRoleExist(selectData.name).then((response) => {
            if (response === 'error') {
              callback(new Error('角色名已存在'))
            } else {
              callback()
            }
          })
        }
      }]
  })

  function GetInfo() {
    console.log('id:' + selectData.id)
    GetRoleEnableMenus(selectData.id).then((response) => {
      console.log(response)
      menus.value = response.menus
      enables.value = response.enable
    })
  }

  async function handleUpdate() {
    let checkedKeys = menuTree.value.getCheckedKeys().concat(menuTree.value.getHalfCheckedKeys())
    console.log(checkedKeys)
    selectData.menus = checkedKeys
    console.log(selectData)
    if (selectData.id === null) {
      try {
        await PostNewRoles(selectData)
        ElNotification({
          title: 'success',
          message: '角色新建成功',
          type: 'success'
        })
      } catch (error) {
        ElNotification({
          title: 'error',
          message: '角色新建失败：' + error,
          type: 'error'
        })
      }
    } else {
      try {
        await PutRoles(selectData)
        ElNotification({
          title: 'success',
          message: '角色更新成功',
          type: 'success'
        })
      } catch (error) {
        ElNotification({
          title: 'error',
          message: '失败：' + error,
          type: 'error'
        })
      }
    }
    visible.value = false
    emit('success')
  }

  function customNodeClass(data, node) {
    if (data.type === 'subPage') {
      return 'is-btn'
    }
    return null
  }

  function add() {
    Object.assign(selectData, {
      id: null,
      name: '',
      description: '',
      enable: true
    })
    GetInfo()
    visible.value = true
  }

  function edit(role) {
    Object.assign(selectData, role)
    GetInfo()
    visible.value = true
  }


  defineExpose({add, edit})

</script>

<style>
.el-tree-node.is-expanded.is-btn > .el-tree-node__children {
  display: flex;
  flex-direction: row;
}
</style>

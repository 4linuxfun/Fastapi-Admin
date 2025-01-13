<template>
  <el-drawer v-model="visible" title="添加子菜单" destroy-on-close>
    <el-alert
      title="菜单填写说明："
      type="warning">
      <template #default>
        <span>一级菜单：菜单路径‘/’开头，前端组件为Layout，如果一级菜单没子菜单，则前端组件为对应组件名</span><br>
        <span>二级菜单：菜单路径为子路由path，前端组件为对应的组件名</span>
      </template>
    </el-alert>
    <el-form :model="selectData" label-width="100px" size="large">
      <el-form-item label="菜单类型:">
        <el-radio-group v-model="selectData.type">
          <el-radio-button value="page">一级菜单</el-radio-button>
          <el-radio-button value="subPage">子菜单</el-radio-button>
          <el-radio-button value="btn">按钮</el-radio-button>
        </el-radio-group>
      </el-form-item>
      <component :is="currentType" v-model:form="selectData"/>
      <el-form-item>
        <el-button type="danger" @click="visible=false">取消</el-button>
        <!-- 更新和添加按钮触发的事件都是一样的，只是提交数据时id字段为空，此需要服务端通过此字段去判断添加还是更新 -->
        <el-button type="primary" @click="handleUpdate" v-if="selectData.id">更新</el-button>
        <el-button type="primary" @click="handleUpdate" v-else>添加</el-button>
      </el-form-item>
    </el-form>

    <!-- 编辑按钮对话框内容 -->
  </el-drawer>
</template>

<script setup>
  import {
    PostNewMenu,
    PutMenu
  } from '@/api/menus'
  import {
    ref,
    reactive, onMounted, computed, watch, shallowRef
  } from 'vue'
  import MenuForm from './MenuForm'
  import ButtonForm from './ButtonForm'
  import {ElNotification} from 'element-plus'

  const emit = defineEmits(['success'])
  const currentType = shallowRef(null)
  const visible = ref(false)
  const selectData = reactive({})

  function changeType(value) {
    if (value === 'btn') {
      currentType.value = ButtonForm
    } else {
      currentType.value = MenuForm
    }
  }

  async function handleUpdate() {
    console.log(selectData)
    if (selectData.id === null) {
      console.log('新建菜单')
      await PostNewMenu(selectData)
    } else {
      await PutMenu(selectData)
      ElNotification({
        message: '更新成功',
        type: 'success'
      })
    }
    visible.value = false
    emit('success')
  }

  function add(parentId, menuType) {
    Object.assign(selectData, {
      id: null,
      parent_id: parentId,
      name: '',
      path: '',
      component: null,
      auth: '',
      enable: 0,
      type: menuType
    })
    visible.value = true
  }

  function edit(row) {
    Object.assign(selectData, row)
    visible.value = true
  }


  watch(selectData, () => {
    changeType(selectData.type)
  })

  onMounted(() => {
    changeType(selectData.type)
  })

  defineExpose({add, edit})
</script>

<style>
</style>

<template>
  <el-form :model="selectData" label-width="100px" size="large">
    <el-form-item label="菜单类型:">
      <el-radio-group v-model="selectData.type">
        <el-radio-button label="page">一级菜单</el-radio-button>
        <el-radio-button label="subPage">子菜单</el-radio-button>
        <el-radio-button label="btn">按钮</el-radio-button>
      </el-radio-group>
    </el-form-item>
    <component :is="currentType" v-model:form="selectData"></component>
    <el-form-item>
      <el-button @click="$emit('update:visible', false)">取消</el-button>
      <!-- 更新和添加按钮触发的事件都是一样的，只是提交数据时id字段为空，此需要服务端通过此字段去判断添加还是更新 -->
      <el-button type="primary" @click="handleUpdate" v-if="selectData.id">更新</el-button>
      <el-button type="primary" @click="handleUpdate" v-else>添加</el-button>
    </el-form-item>
  </el-form>

  <!-- 编辑按钮对话框内容 -->
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

  const currentType = shallowRef(null)

  const props = defineProps(['data', 'visible'])
  const emit = defineEmits(['update:visible'])
  const selectData = reactive(props.data)

  function changeType(value) {
    if (value === 'btn') {
      currentType.value = ButtonForm
    } else {
      currentType.value = MenuForm
    }
  }

  const handleUpdate = () => {
    console.log(selectData)
    if (selectData.id === null) {
      console.log('新建菜单')
      PostNewMenu(selectData)
    } else {
      PutMenu(selectData).then(response => {
        ElNotification({
          message: '更新成功',
          type: 'success'
        })
      })
    }
    emit('update:visible', false)
  }


  watch(() => selectData.type, (newValue, preValue) => {
    changeType(newValue)
  })

  onMounted(() => {
    changeType(selectData.type)
  })
</script>

<style>
</style>

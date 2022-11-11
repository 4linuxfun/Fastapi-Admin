<template>
  <el-form v-model="form" label-width="100px">
    <el-form-item label="名称" prop="name">
      <el-input v-model="form.label"/>
    </el-form-item>
    <el-form-item label="数据值" prop="data">
      <el-input v-model="form.value"/>
    </el-form-item>
    <el-form-item label="描述" prop="desc">
      <el-input v-model="form.desc"/>
    </el-form-item>
    <el-form-item label="排序值" prop="sort">
      <el-input v-model="form.sort"/>
    </el-form-item>
    <el-form-item label="是否启用" prop="enable">
      <el-switch v-model="form.enable"/>
    </el-form-item>
  </el-form>
  <el-button @click="$emit('update:visible',false)">关闭</el-button>
  <el-button type="primary" @click="handleAdd">确定</el-button>
</template>

<script setup>

  import {reactive} from 'vue'
  import {PostNewDictItem, PutDictItem} from '@/api/dictonary'
  import {ElNotification} from 'element-plus'

  const props = defineProps(['item', 'visible'])
  const emit = defineEmits(['update:visible'])
  const form = reactive(props.item)

  function handleAdd() {
    if (form.id === null) {
      PostNewDictItem(form).then(() => {
        ElNotification({
          title: 'success',
          message: '字典元素添加成功',
          type: 'success'
        })
      })
    } else {
      PutDictItem(form).then(() => {
        ElNotification({
          title: 'success',
          message: '字典元素更新成功',
          type: 'success'
        })
      })
    }

    emit('update:visible', false)
  }
</script>

<style scoped>

</style>
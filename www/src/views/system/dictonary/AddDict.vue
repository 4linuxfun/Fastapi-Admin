<template>
  <el-form :model="form" label-width="100px">
    <el-form-item label="字典名字：" prop="name">
      <el-input v-model="form.name"/>
    </el-form-item>
    <el-form-item label="字典编码：" prop="code">
      <el-input v-model="form.code"/>
    </el-form-item>
    <el-form-item label="描述：" prop="desc">
      <el-input v-model="form.desc"/>
    </el-form-item>
  </el-form>
  <el-button type="danger" @click="$emit('update:visible',false)">关闭</el-button>
  <el-button type="primary" @click="handleAdd">确定</el-button>
</template>

<script setup>

  import {reactive} from 'vue'
  import {PostNewDict} from '@/api/dictonary'
  import {ElNotification} from 'element-plus'

  const props = defineProps(['dict','visible'])
  const emit = defineEmits(['update:visible'])
  const form = reactive(props.dict)

  function handleAdd() {
    PostNewDict(form).then(() => {
      ElNotification({
        title: 'success',
        message: '数据字典添加成功',
        type: 'success'
      })
    })
    emit('update:visible', false)
  }

</script>

<style scoped>

</style>
<template>
  <el-dialog v-model="visible" width="30%" destroy-on-close>
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
        <el-switch v-model="form.enable" style="--el-switch-on-color: #13ce66; --el-switch-off-color: #ff4949"/>
      </el-form-item>
    </el-form>
    <el-button @click="$emit('update:visible',false)">关闭</el-button>
    <el-button type="primary" @click="handleAdd">确定</el-button>
  </el-dialog>
</template>

<script setup>

  import {ref, reactive} from 'vue'
  import {PostNewDictItem, PutDictItem} from '@/api/dictonary'
  import {ElNotification} from 'element-plus'

  const emit = defineEmits(['success'])
  const visible = ref(false)
  const form = reactive({})

  async function handleAdd() {
    if (form.id === null) {
      try {
        await PostNewDictItem(form)
        ElNotification({
          title: 'success',
          message: '字典元素添加成功',
          type: 'success'
        })
      } catch (e) {
        ElNotification({
          title: 'error',
          message: '字典元素添加失败',
          type: 'error'
        })
      }
    } else {
      try {
        await PutDictItem(form)
        ElNotification({
          title: 'success',
          message: '字典元素更新成功',
          type: 'success'
        })
      } catch (e) {
        ElNotification({
          title: 'error',
          message: '字典元素更新失败',
          type: 'error'
        })
      }
    }
    visible.value = false
    emit('success')
  }

  function add(dictId) {
    Object.assign(form, {
      id: null,
      label: null,
      value: null,
      desc: null,
      sort: 1,
      enable: true,
      dict_id: dictId
    })
    visible.value = true
  }

  function edit(dictItem) {
    Object.assign(form, dictItem)
    visible.value = true
  }

  defineExpose({add, edit})
</script>

<style scoped>

</style>
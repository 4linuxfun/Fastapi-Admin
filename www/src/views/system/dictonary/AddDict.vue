<template>
  <el-form :model="form" :rules="rules" label-width="100px" ref="formRef">
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
  <el-button type="danger" @click="$emit('update:visible', false)"
  >关闭
  </el-button
  >
  <el-button type="primary" @click="handleAdd">确定</el-button>
</template>

<script setup>
  import {reactive, ref} from 'vue'
  import {PostNewDict, PutDict} from '@/api/dictonary'
  import {ElNotification} from 'element-plus'

  const props = defineProps(['dict', 'visible'])
  const emit = defineEmits(['update:visible'])
  const form = reactive(props.dict)
  const formRef = ref(null)

  const rules = {
    name: [{required: true, message: '字典名称不能为空', trigger: 'blur'}],
    code: [{required: true, message: '字典编码不能为空', trigger: 'blur'}],
  }

  function handleAdd() {
    formRef.value.validate((valid) => {
      if (valid) {
        // 验证通过
        if (form.id === null) {
          PostNewDict(form).then(() => {
            ElNotification({
              title: 'success',
              message: '数据字典添加成功',
              type: 'success',
            })
          })
        } else {
          PutDict(form).then(() => {
            ElNotification({
              title: 'success',
              message: '数据字典更新成功',
              type: 'success',
            })
          })
        }

        emit('update:visible', false)
      } else {
        // 验证不通过
        ElNotification({
          title: 'error',
          message: '请填写必填项',
          type: 'error',
        })
      }
    })
  }
</script>

<style scoped></style>

<template>
  <el-form :model="form" ref="ruleFormRef" label-width="100px" :rules="rules">
    <el-form-item label="用户名:">
      <el-input v-model="userName" disabled></el-input>
    </el-form-item>
    <el-form-item label="登录密码:" prop="password">
      <el-input v-model="form.password" placeholder="请输入登录密码" show-password></el-input>
    </el-form-item>
    <el-form-item label="确认密码:" prop="secondPassword">
      <el-input v-model="form.secondPassword" placeholder="请重新输入登录密码" show-password></el-input>
    </el-form-item>
  </el-form>
  <el-button @click="$emit('update:visible',false)">关闭</el-button>
  <el-button @click="updatePasswd(ruleFormRef)" type="primary">确定</el-button>
</template>

<script setup>
  import {ResetPasswd} from '@/api/users'
  import {ElNotification} from 'element-plus'
  import md5 from 'js-md5'
  import {computed, reactive, toRefs, ref} from 'vue'

  const props = defineProps(['user', 'visible'])
  const emit = defineEmits(['update:visible'])
  const {user} = toRefs(props)
  const form = reactive({
    password: null,
    secondPassword: null,
  })
  console.log(user)

  const ruleFormRef = ref()

  const userName = computed(() => user.value.name)
  const userId = computed(() => user.value.id)
  const checkPassword = (rule, value, callback) => {
    console.log(form)
    console.log(value)
    if (value.length === 0) {
      callback(new Error('请确认密码不能为空'))
    } else if (value !== form.password) {
      callback(new Error('2次密码不一致'))
    } else {
      callback()
    }
  }

  const rules = {
    password: [{required: true, trigger: 'blur', message: '请输入密码'}],
    secondPassword: [{required: true, trigger: 'blur', message: '请再次输入密码进行确认'},
      {validator: checkPassword, trigger: 'blur'}]
  }

  function updatePasswd(formEl) {
    console.log(userId)
    console.log(form.password)
    formEl.validate((valid) => {
      if (valid) {
        console.log('submit')
        ResetPasswd(userId.value, md5(form.password)).then(() => {
          ElNotification({
            title: 'success',
            message: '密码重置成功',
            type: 'success'
          })
        }).catch(error => {
          ElNotification({
            title: '错误',
            message: '密码重置失败：' + error,
            type: 'error'
          })
        })
        emit('update:visible', false)
      } else {
        console.log('error')
        return false
      }
    })

  }

</script>

<style scoped>

</style>
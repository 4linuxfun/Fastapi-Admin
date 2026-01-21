<template>
  <el-dialog v-model="visible" title="用户密码重置" width="30%" destroy-on-close>
    <el-form ref="ruleFormRef" :model="form" label-width="100px" :rules="rules">
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
    <el-button @click="visible=false">关闭</el-button>
    <el-button @click="updatePasswd" type="primary">确定</el-button>
  </el-dialog>
</template>

<script setup>
  import {ResetPasswd} from '@/api/users'
  import {ElNotification} from 'element-plus'
  import md5 from 'js-md5'
  import {computed, reactive, ref} from 'vue'

  const visible = ref(false)
  const user = ref(null)
  const form = reactive({})
  const ruleFormRef = ref(null)

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

  async function updatePasswd() {
    console.log(userId)
    await ruleFormRef.value.validate(async (valid) => {
      if (valid) {
        console.log('submit')
        try {
          await ResetPasswd(userId.value, md5(form.password))
          ElNotification({
            title: 'success',
            message: '密码重置成功',
            type: 'success'
          })
        } catch {
          ElNotification({
            title: '错误',
            message: '密码重置失败：' + error,
            type: 'error'
          })
        }
        visible.value = false
      }
    })
  }

  function reset(resetUser) {
    Object.assign(form, {
      password: null,
      secondPassword: null,
    })
    user.value = resetUser
    visible.value = true
  }

  defineExpose({reset,})

</script>

<style scoped>

</style>
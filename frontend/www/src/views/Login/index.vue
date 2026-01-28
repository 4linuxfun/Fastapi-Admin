<template>
  <div class="login">
    <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" label-position="left" label-width="0px"
      class="login-form" @keyup.enter="handleLogin">
      <h2 class="login-title">FastAPI Admin后台</h2>
      <el-form-item prop="username">
        <el-input v-model="loginForm.username" type="text" auto-complete="off" placeholder="请输入用户名">
          <template #prepend>
            <el-icon :size="20">
              <user />
            </el-icon>
          </template>
        </el-input>
      </el-form-item>
      <el-form-item prop="password">
        <el-input v-model="loginForm.password" type="password" auto-complete="off" placeholder="请输入密码">
          <template #prepend>
            <el-icon :size="20">
              <lock />
            </el-icon>
          </template>
        </el-input>
      </el-form-item>
      <!-- 添加验证码输入框 -->
      <el-form-item prop="captcha_code">
        <el-input v-model="loginForm.captcha_code" type="text" auto-complete="off" placeholder="请输入验证码">
          <template #prepend>
            <el-icon :size="20">
              <key/>
            </el-icon>
          </template>
          <template #append>
            <img :src="captchaSrc" @click="refreshCaptcha" alt="验证码" style="cursor: pointer; height: 38px; width: auto; object-fit: contain;">
          </template>
        </el-input>
      </el-form-item>
      <el-checkbox v-model="loginForm.rememberMe" style="margin: 0px 0px 25px 0px">记住账号</el-checkbox>
      <el-form-item style="width: 100%">
        <el-button :loading="loading" type="primary" style="width: 100%" @click="handleLogin">
          <span v-if="!loading">登 录</span>
          <span v-else>登 录 中...</span>
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ElNotification } from 'element-plus'
import {
  User,
  Lock,
  Key // 添加Key图标
} from '@element-plus/icons-vue'
import Cookies from 'js-cookie'
import md5 from 'js-md5'
import {
  useStore
} from '@/stores'

import { onMounted, reactive, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

const loginForm = reactive({
  username: '',
  password: '',
  rememberMe: false,
  captcha_code: '',
  captcha_key: ''
})

const loginRules = reactive({
  username: [{
    required: true,
    trigger: 'blur',
    message: '用户名不能为空'
  }],
  password: [{
    required: true,
    trigger: 'blur',
    message: '密码不能为空'
  }],
  captcha_code: [{
    required: true,
    trigger: 'blur',
    message: '验证码不能为空'
  }]
})

const loading = ref(false)
const store = useStore()
const loginFormRef = ref(null)

const router = useRouter()
const route = useRoute()

const captchaSrc = ref('')

function getCookie() {
  const username = Cookies.get('username')
  const rememberMe = Cookies.get('rememberMe')
  Object.assign(loginForm, {
    username: username === undefined ? '' : username,
    rememberMe: rememberMe === undefined ? false : Boolean(rememberMe),
  })
}

function handleLogin() {
  loginFormRef.value.validate((valid) => {
    let password = md5(loginForm.password)
    const user = {
      username: loginForm.username,
      password: password,
      rememberMe: loginForm.rememberMe,
      captcha_code: loginForm.captcha_code,
      captcha_key: loginForm.captcha_key
    }
    console.log('start to do login')
    if (valid) {
      loading.value = true
      if (user.rememberMe) {
        Cookies.set('username', user.username, {
          expires: 1
        })
        Cookies.set('rememberMe', user.rememberMe, {
          expires: 1
        })
      } else {
        Cookies.remove('username')
        Cookies.remove('rememberMe')
      }
      console.log('dispatch login store actions')
      store.logIn(user).then(() => {
        console.log('login ok,start to redirect to home')
        let redirect = '/'
        if (route.query.redirect) {
          redirect = route.query.redirect
        }
        router.push({
          path: redirect
        })
      }).catch(error => {
        console.log('login failed', error)
        refreshCaptcha() // 刷新验证码
      }).finally(() => {
        loading.value = false
      })
    } else {
      console.log('提交错误!')
      return false
    }
  })
}

function refreshCaptcha() {
  axios.get('/api/captcha').then(res => {
    if (res.data.code === 200) {
      captchaSrc.value = res.data.data.image_base64
      loginForm.captcha_key = res.data.data.captcha_key
    }
  })
}

onMounted(() => {
  getCookie()
  refreshCaptcha()
})
</script>

<style rel="stylesheet/scss" lang="scss">
.login {
  display: flex;
  justify-content: center;
  align-items: center;
  // background-image:url('../../assets/login_images/1.jpg');
  height: 100%;
}

.login-title {
  margin: 0px auto 40px auto;
  text-align: center;
  font-size: 30px;
  font-weight: bold;
  color: white;
}

.login-form {
  border-radius: 6px;
  background: #B3C0D1;
  width: 365px;
  padding: 25px 25px 5px 25px;

  .el-input {
    height: 38px;

    input {
      height: 38px;
    }
  }
}

.login-tip {
  font-size: 13px;
  text-align: center;
  color: #bfbfbf;
}
</style>

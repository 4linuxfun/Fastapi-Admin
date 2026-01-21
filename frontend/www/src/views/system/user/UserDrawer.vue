<template>
  <el-drawer v-model="visible" title="编辑用户" destroy-on-close>
    <el-form ref="userFormRef" :model="selectData" label-width="80px" :rules="rules">
      <el-form-item label="用户名称" prop="name">
        <el-input v-model="selectData.name" :disabled="selectData.id !== null"></el-input>
      </el-form-item>
      <el-form-item label="状态">
        <auto-dict dict-type="switch" code="enable_code" v-model="selectData.enable" />
      </el-form-item>
      <el-form-item label="角色">
        <el-checkbox-group v-model="enableRoleList">
          <el-checkbox v-for="role in roleList" :value="role.id" :label="role.name" :key="role.id"
            :disabled="!role.enable" />
        </el-checkbox-group>
      </el-form-item>
      <el-form-item>
        <el-button @click="visible = false">取消</el-button>
        <el-button v-if="selectData.id" type="primary" @click="handleUpdate">更新</el-button>
        <el-button v-else type="primary" @click="handleUpdate">添加</el-button>
      </el-form-item>
    </el-form>
  </el-drawer>
</template>

<script setup>
import {
  GetUserExist, GetUserInfo,
  GetUserRoles, PostAddUser, PutNewUser
} from '@/api/users'
import { ElNotification } from 'element-plus'
import { reactive, ref, toRefs } from 'vue'
import { GetDictItems } from '@/api/dictonary'
import AutoDict from '@/components/AutoDict'

const emit = defineEmits(['success'])
const selectData = reactive({})
console.log(selectData)
const visible = ref(false)
const userFormRef = ref(null)
const roleList = ref([])
const enableRoleList = ref([])

const rules = reactive({
  name: [{ required: true, trigger: 'blur', message: '请输入用户名' },
  {
    required: true, trigger: 'blur',
    validator: (rule, value, callback) => {
      GetUserExist(selectData.name).then((response) => {
        if (response === 'error') {
          callback(new Error('用户名:' + selectData.name + '已存在'))
        } else {
          callback()
        }
      })
    }
  }]
})


async function handleUpdate() {
  console.log(selectData)
  if (selectData.id === null) {
    try {
      await userFormRef.value.validate()
    } catch (error) {
      ElNotification({
        title: 'error',
        message: '存在信息错误',
        type: 'error'
      })
      return
    }
    await PostAddUser(selectData, enableRoleList.value)
    ElNotification({
      title: 'success',
      message: '用户新建成功',
      type: 'success'
    })
  } else {
    console.log(enableRoleList)
    await PutNewUser(selectData, enableRoleList.value)
    console.log('update ok')
    ElNotification({
      title: 'success',
      message: '用户更新成功',
      type: 'success'
    })
  }
  console.log('visible')
  visible.value = false
  emit('success')
}


async function add() {
  Object.assign(selectData, {
    id: null,
    name: null,
    email: '',
    enable: 0,
    avatar: '',
    password: null,
  })
  let userRoles = await GetUserRoles(selectData.id)
  roleList.value = userRoles.roles
  enableRoleList.value = userRoles.enable
  visible.value = true
}

async function edit(uid) {
  try {
    let response = await GetUserInfo(uid)
    Object.assign(selectData, response)
    let userRoles = await GetUserRoles(selectData.id)
    roleList.value = userRoles.roles
    enableRoleList.value = userRoles.enable
    visible.value = true
  } catch (err) {
    console.log('获取组失败。。。')
    return false
  }

}


defineExpose({
  add, edit
})
</script>

<style></style>

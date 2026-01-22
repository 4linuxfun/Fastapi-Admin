<template>
  <el-drawer v-model="visible" title="编辑用户" destroy-on-close>
    <el-form ref="userFormRef" :model="selectData" label-width="80px" :rules="rules">
      <el-form-item label="用户头像" prop="avatar">
        <el-upload
          class="avatar-uploader"
          :action="uploadUrl"
          :headers="headers"
          :show-file-list="false"
          :on-success="handleAvatarSuccess"
          :before-upload="beforeAvatarUpload"
          accept="image/*"
          :data="{tag: 'avatar'}"
          name="file">
          <img v-if="selectData.avatar" :src="selectData.avatar" class="avatar" />
          <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
        </el-upload>
      </el-form-item>
      <el-form-item label="用户名称" prop="name">
        <el-input v-model="selectData.name" :disabled="selectData.id !== null" autocomplete="off"></el-input>
      </el-form-item>
      <el-form-item label="密码" prop="password" v-if="!selectData.id">
        <el-input v-model="selectData.password" type="password" show-password autocomplete="new-password"></el-input>
      </el-form-item>
      <el-form-item label="用户邮箱" prop="email">
        <el-input v-model="selectData.email"></el-input>
      </el-form-item>
      <el-form-item label="角色">
        <el-checkbox-group v-model="enableRoleList">
          <el-checkbox v-for="role in roleList" :value="role.id" :label="role.name" :key="role.id"
            :disabled="!role.enable" />
        </el-checkbox-group>
      </el-form-item>
      <el-form-item label="状态">
        <auto-dict dict-type="switch" code="enable_code" v-model="selectData.enable" />
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
import { reactive, ref, toRefs, computed } from 'vue'
import { GetDictItems } from '@/api/dictonary'
import AutoDict from '@/components/AutoDict'
import { Plus } from '@element-plus/icons-vue'
import { useUpload } from '@/composables/useUpload'
import md5 from 'js-md5'

const emit = defineEmits(['success'])
const selectData = reactive({})
console.log(selectData)
const visible = ref(false)
const userFormRef = ref(null)
const roleList = ref([])
const enableRoleList = ref([])

const { uploadUrl, headers, handleUploadSuccess: onUploadSuccess } = useUpload()

const handleAvatarSuccess = (response, uploadFile) => {
  const urls = onUploadSuccess(response)
  if (urls) {
    selectData.avatar = urls[0]
  }
}

const beforeAvatarUpload = (rawFile) => {
  if (rawFile.type.indexOf('image/') === -1) {
    ElNotification.error('头像必须是图片格式!')
    return false
  }
  return true
}

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
  }],
  password: [{ required: true, trigger: 'blur', message: '请输入密码' }]
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
    // Hash password before sending
    const dataToSend = { ...selectData }
    dataToSend.password = md5(dataToSend.password)
    
    await PostAddUser(dataToSend, enableRoleList.value)
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

<style>
.avatar-uploader .el-upload {
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
}

.avatar-uploader .el-upload:hover {
  border-color: var(--el-color-primary);
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 100px;
  height: 100px;
  text-align: center;
}
.avatar {
  width: 100px;
  height: 100px;
  display: block;
}
</style>

<template>
  <el-form :model="selectData" label-width="80px">
    <el-form-item label="用户名称" prop="name">
      <el-input v-model="selectData.name" :disabled="selectData.id !== null"></el-input>
    </el-form-item>
    <el-form-item label="状态">
      <el-switch v-model="selectData.enable"  style="--el-switch-on-color: #13ce66; --el-switch-off-color: #ff4949"/>
    </el-form-item>
    <el-form-item label="角色">
      <el-checkbox-group v-model="enableRoleList">
        <el-checkbox v-for="role in roleList" :label="role.id" :key="role.id"
                     :disabled="!role.enable">{{ role.name }}
        </el-checkbox>
      </el-checkbox-group>
    </el-form-item>
    <el-form-item>
      <el-button @click="$emit('update:visible',false)">取消</el-button>
      <el-button v-if="selectData.id" type="primary" @click="handleUpdate">更新</el-button>
      <el-button v-else type="primary" @click="handleUpdate">添加</el-button>
    </el-form-item>
  </el-form>

</template>

<script setup>
  import {
    GetUserRoles, PostAddUser, PutNewUser
  } from '@/api/users'
  import {ElNotification} from 'element-plus'
  import {onMounted, reactive, ref, toRefs} from 'vue'
  import {GetDictItems} from '@/api/dictonary'

  const props = defineProps(['user', 'visible'])
  const emit = defineEmits(['update:visible'])
  const {user} = toRefs(props)
  const selectData = reactive(JSON.parse(JSON.stringify(user.value)))
  console.log(selectData)
  const roleList = ref([])
  const enableRoleList = ref([])
  const selectOptions = ref(null)

  const getRoles = (userId) => {
    console.log(selectData)
    GetUserRoles(userId).then((response) => {
      roleList.value = response.roles
      enableRoleList.value = response.enable
    })
  }

  const handleUpdate = () => {
    console.log(selectData)
    // this.$emit('update:user', this.selectData, this.enableRoleList)
    if (selectData.id === null) {
      PostAddUser(selectData, enableRoleList.value).then(() => {
        ElNotification({
          title: 'success',
          message: '用户新建成功',
          type: 'success'
        })
      })
    } else {
      console.log(enableRoleList)
      PutNewUser(selectData, enableRoleList.value).then(() => {
        ElNotification({
          title: 'success',
          message: '用户更新成功',
          type: 'success'
        })
      })
    }
    emit('update:visible', false)
  }

  onMounted(() => {
    GetDictItems('enable_code').then(response => {
      selectOptions.value = response
    })
    getRoles(selectData.id)
  })

</script>

<style>
</style>

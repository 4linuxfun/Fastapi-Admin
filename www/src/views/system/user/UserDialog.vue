<template>
  <el-form :model="selectData" label-width="80px">
    <el-form-item label="用户名称" prop="name">
      <el-input v-model="selectData.name" :disabled="selectData.id !== null"></el-input>
    </el-form-item>
    <el-form-item label="状态">
      <el-radio-group v-model="selectData.enable">
        <el-radio :label="0">禁用</el-radio>
        <el-radio :label="1">启用</el-radio>
      </el-radio-group>
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

<script>
  import {
    GetUserRoles,
    GetUserExist, PostAddUser, PutNewUser
  } from '@/api/users'
  import md5 from 'js-md5'
  import {ElNotification} from 'element-plus'
  import {reactive, ref, toRefs} from 'vue'

  export default {
    props: ['user', 'visible'],
    emits: ['update:visible'],
    setup(props, {emit}) {
      const {user} = toRefs(props)
      const selectData = reactive(JSON.parse(JSON.stringify(user.value)))
      console.log(selectData)
      const roleList = ref([])
      const enableRoleList = ref([])

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

      getRoles(selectData.id)
      return {
        selectData,
        roleList,
        enableRoleList,
        getRoles,
        handleUpdate
      }
    }
  }
</script>

<style>
</style>

<template>
  <el-dialog :model-value="visible" title="用户编辑页面" width="30%" @close="$emit('update:visible',false)"
             @opened="getRoles(selectData.id)" destroy-on-close>
    <el-form :model="selectData" label-width="80px" :rules="rules">
      <el-form-item label="用户名称" prop="name">
        <el-input v-model="selectData.name" :disabled="selectData.id !== null"></el-input>
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input v-model="selectData.password" placeholder="请输入新密码" :show-password="true"></el-input>
      </el-form-item>
      <el-form-item label="密码确认" prop="secondPassword">
        <el-input v-model="selectData.secondPassword" placeholder="请再次确认密码" :show-password="true"></el-input>
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
  </el-dialog>

</template>

<script>
  import {
    GetUserRoles,
    GetUserExist, PostAddUser, PutNewUser
  } from '@/api/users'
  import md5 from 'js-md5'
  import {ElNotification} from 'element-plus'

  export default {
    props: ['user', 'visible'],
    emits: ['update:visible'],
    data() {
      function checkPassword(rule, value, callback) {
        console.log(this.selectData)
        console.log(value)
        console.log(this.selectData.password)
        if (value.length === 0) {
          callback(new Error('请确认密码不能为空'))
        } else if (value !== this.selectData.password) {
          callback(new Error('2次密码不一致'))
        } else {
          callback()
        }
      }

      return {
        selectData: JSON.parse(JSON.stringify(this.user)),
        roleList: [],
        enableRoleList: [],
        password: null,
        secondPassword: null,
        rules: {
          name: [{
            required: true,
            message: '请输入用户名',
            trigger: 'blur',
          }, {
            trigger: 'blur',
            validator(rule, value, callback) {
              GetUserExist(value).then(() => {
                callback()
              }).catch((error) => {
                callback(error)
              })
            },
          }],
          password: [{message: '密码不能为空', trigger: 'blur'}],
          secondPassword: [{validator: checkPassword, trigger: 'blur'}]
        }
      }
    },
    methods:
        {
          getRoles(userId) {
            console.log(this.selectData)
            GetUserRoles(userId).then((response) => {
              this.roleList = response.roles
              this.enableRoleList = response.enable
            })
          },
          handleUpdate() {
            if (this.password) {
              console.log(md5(this.password))
              this.selectData['password'] = md5(this.password)
            }
            console.log(this.selectData)
            // this.$emit('update:user', this.selectData, this.enableRoleList)
            if (this.selectData.id === null) {
              PostAddUser(this.selectData, this.enableRoleList).then(() => {
                ElNotification({
                  title: 'success',
                  message: '用户新建成功',
                  type: 'success'
                })
              })
            } else {
              console.log(this.enableRoleList)
              PutNewUser(this.selectData, this.enableRoleList).then(() => {
                ElNotification({
                  title: 'success',
                  message: '用户更新成功',
                  type: 'success'
                })
              })
            }
            this.$emit('update:visible', false)

          }
        }
    ,
  }
</script>

<style>
</style>

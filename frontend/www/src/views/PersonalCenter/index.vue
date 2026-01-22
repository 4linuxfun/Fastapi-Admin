<template>
  <el-row :gutter="20">
    <!-- Left Column: User Profile Card -->
    <el-col :span="6">
      <el-card class="box-card">
        <template #header>
          <div class="clearfix">
            <span>个人信息</span>
          </div>
        </template>
        <div class="user-profile">
          <div class="box-center" style="text-align: center">
            <el-avatar :size="100" :src="userInfo.avatar || 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif'" />
          </div>
          <div class="box-center" style="text-align: center; padding-top: 10px">
            <div class="user-name text-center">{{ userInfo.name }}</div>
            <div class="user-role text-center text-muted">{{ roleNames }}</div>
          </div>
        </div>
        
        <div class="user-bio">
          <div class="user-education user-bio-section">
            <div class="user-bio-section-header"><el-icon><User /></el-icon><span> 用户名称</span></div>
            <div class="user-bio-section-body">
              <div class="text-muted">{{ userInfo.name }}</div>
            </div>
          </div>
          

          
           <div class="user-education user-bio-section">
            <div class="user-bio-section-header"><el-icon><Message /></el-icon><span> 用户邮箱</span></div>
            <div class="user-bio-section-body">
              <div class="text-muted">{{ userInfo.email || '未设置' }}</div>
            </div>
          </div>
          

          
          <div class="user-education user-bio-section">
            <div class="user-bio-section-header"><el-icon><Files /></el-icon><span> 所属角色</span></div>
            <div class="user-bio-section-body">
              <div class="text-muted">{{ roleNames }}</div>
            </div>
          </div>
          

          
        </div>
      </el-card>
    </el-col>
    
    <!-- Right Column: Settings Tabs -->
    <el-col :span="18">
      <el-card>
        <template #header>
          <div class="clearfix">
            <span>基本资料</span>
          </div>
        </template>
        <el-tabs v-model="activeTab">
          <!-- Basic Info Tab -->
          <el-tab-pane label="基本资料" name="basic">
            <el-form ref="userFormRef" :model="userForm" label-width="80px">
              <el-form-item label="用户昵称" prop="name">
                <el-input v-model="userForm.name" :disabled="userInfo.name === 'admin'" />
              </el-form-item>

              <el-form-item label="邮箱" prop="email">
                <el-input v-model="userForm.email" />
              </el-form-item>

              <el-form-item>
                <el-button type="primary" @click="submitUserInfo">保存</el-button>
                <el-button type="danger">关闭</el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>
          
          <!-- Password Tab -->
          <el-tab-pane label="修改密码" name="password">
             <el-form ref="pwdFormRef" :model="pwdForm" :rules="pwdRules" label-width="80px">
               <el-form-item label="新密码" prop="password">
                 <el-input v-model="pwdForm.password" show-password />
               </el-form-item>
               <el-form-item label="确认密码" prop="confirmPassword">
                 <el-input v-model="pwdForm.confirmPassword" show-password />
               </el-form-item>
               <el-form-item>
                 <el-button type="primary" @click="submitPassword">保存</el-button>
                 <el-button type="danger">关闭</el-button>
               </el-form-item>
             </el-form>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { User, Message, Files } from '@element-plus/icons-vue'
import { useStore } from '@/stores'
import { GetUserInfo, PutNewUser, ResetPasswd } from '@/api/users'
import { ElMessage } from 'element-plus'
import md5 from 'js-md5'

const store = useStore()
const activeTab = ref('basic')
const userFormRef = ref(null)
const pwdFormRef = ref(null)



const userForm = reactive({
  id: null,
  name: '',
  email: '',
  avatar: '',
  roles: [], // full role objects
  enable: true
})

const userInfo = reactive({
  id: null,
  name: '',
  email: '',
  avatar: '',
  roles: [],
  enable: true
})

const pwdForm = reactive({
  password: '',
  confirmPassword: ''
})

const pwdRules = {
  password: [{ required: true, message: '请输入新密码', trigger: 'blur' }, { min: 6, message: '密码长度不能小于6位', trigger: 'blur' }],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== pwdForm.password) {
          callback(new Error('两次输入密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const roleNames = computed(() => {
  if (!userInfo.roles || userInfo.roles.length === 0) return '暂无角色'
  return userInfo.roles.map(r => r.name).join(' / ')
})

const getUser = async () => {
    try {
        const uid = store.uid || localStorage.getItem('uid') // Fallback if store invalid
        if (!uid) return
        const res = await GetUserInfo(uid)
        // Adjust response data structure if needed
        const data = res
        userForm.id = data.id
        userForm.name = data.name
        userForm.email = data.email
        userForm.avatar = data.avatar
        userForm.roles = data.roles || []
        userForm.enable = data.enable

        // Initialize display data
        userInfo.id = data.id
        userInfo.name = data.name
        userInfo.email = data.email
        userInfo.avatar = data.avatar
        userInfo.roles = data.roles || []
        userInfo.enable = data.enable
    } catch (error) {
        console.error(error)
    }
}

const submitUserInfo = async () => {
    try {
        // Construct payload for PutNewUser. API expects {user: ..., roles: [id, id]}
        // We reuse existing roles IDs to avoid changing them
        const roleIds = userForm.roles.map(r => r.id)
        
        await PutNewUser(userForm, roleIds)
        ElMessage.success('个人信息更新成功')
        // Refresh local store info if needed
        store.name = userForm.name
        store.avatar = userForm.avatar
        
        // Update display data on success
        userInfo.name = userForm.name
        userInfo.email = userForm.email
        userInfo.avatar = userForm.avatar
    } catch (error) {
        console.error(error)
        // ElMessage.error handled by request interceptor usually, or add here
    }
}

const submitPassword = async () => {
    if (!userForm.id) return
    pwdFormRef.value.validate(async (valid) => {
        if (valid) {
             try {
                 await ResetPasswd(userForm.id, md5(pwdForm.password))
                 ElMessage.success('密码重置成功')
                 pwdForm.password = ''
                 pwdForm.confirmPassword = ''
             } catch (error) {
                 console.error(error)
             }
        }
    })
}

onMounted(() => {
    getUser()
})

</script>

<style scoped>
.box-card {
  margin-bottom: 20px;
}

.user-profile {
  .user-name {
    font-weight: bold;
  }
  .box-center {
    padding-top: 10px;
  }
  .user-role {
    padding-top: 10px;
    font-weight: 400;
    font-size: 14px;
  }
  .box-social {
    padding-top: 30px;
    .el-table {
      border-top: 1px solid #dfe6ec;
    }
  }
  .user-follow {
    padding-top: 20px;
  }
}

.user-bio {
  margin-top: 20px;
  color: #606266;
  span {
    padding-left: 4px;
  }
  .user-bio-section {
    font-size: 14px;
    padding: 15px 0;
    .user-bio-section-header {
      border-bottom: 1px solid #dfe6ec;
      padding-bottom: 10px;
      margin-bottom: 10px;
      font-weight: bold;
    }
  }
}
.text-muted {
    color: #777;
}
</style>
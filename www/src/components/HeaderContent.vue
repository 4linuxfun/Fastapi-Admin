<template>
  <el-row justify="end">
    <el-col :span="2" style="text-align: right">
      <el-dropdown @command="handleCommand">
        <el-avatar shape="square" :size="50">{{ userName }}</el-avatar>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item>个人中心</el-dropdown-item>
            <el-dropdown-item command="logout">退出</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </el-col>
  </el-row>
</template>

<script setup>
  import {ElMessage, ElMessageBox} from 'element-plus'
  import {useRouter} from 'vue-router'
  import {useStore} from '@/stores'
  import {computed} from 'vue'

  const store = useStore()
  const userName = computed(() => store.name)
  const router = useRouter()

  function handleCommand(command) {
    if (command === 'logout') {
      logOut()
    }
  }

  function logOut() {
    const store = useStore()
    console.log('click logout button')
    ElMessageBox.confirm('确定退出系统吗？', '提示', {
      confirmButtonText: '是',
      cancelButtonText: '否',
      type: 'warning'
    }).then(() => {
      store.logOut()
      router.push('/login')
      ElMessage({
        type: 'success',
        message: '退出成功！'
      })
    }).catch(() => {
      ElMessage({
        type: 'info',
        message: '取消退出'
      })
    })
  }

</script>
<style lang="">

</style>

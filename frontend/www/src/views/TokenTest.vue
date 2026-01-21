<template>
  <div class="token-test">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>Token自动刷新测试</span>
        </div>
      </template>
      
      <div class="token-info">
        <el-descriptions title="Token信息" :column="1" border>
          <el-descriptions-item label="当前Token">
            <el-text class="token-text" type="info">{{ currentToken || '无' }}</el-text>
          </el-descriptions-item>
          <el-descriptions-item label="Token状态">
            <el-tag :type="tokenStatus.type">{{ tokenStatus.text }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="剩余时间">
            <el-text :type="remainingTime > 300 ? 'success' : 'warning'">
              {{ formatTime(remainingTime) }}
            </el-text>
          </el-descriptions-item>
          <el-descriptions-item label="管理器状态">
            <el-tag :type="managerActive ? 'success' : 'danger'">
              {{ managerActive ? '运行中' : '已停止' }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      
      <div class="actions" style="margin-top: 20px;">
        <el-button type="primary" @click="checkTokenStatus">检查Token状态</el-button>
        <el-button type="warning" @click="manualRefresh">手动刷新Token</el-button>
        <el-button type="info" @click="testApiCall">测试API调用</el-button>
        <el-button type="success" @click="startManager" v-if="!managerActive">启动管理器</el-button>
        <el-button type="danger" @click="stopManager" v-if="managerActive">停止管理器</el-button>
      </div>
      
      <div class="logs" style="margin-top: 20px;">
        <el-divider>操作日志</el-divider>
        <el-scrollbar height="200px">
          <div v-for="(log, index) in logs" :key="index" class="log-item">
            <el-text :type="log.type" size="small">
              [{{ log.time }}] {{ log.message }}
            </el-text>
          </div>
        </el-scrollbar>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { getToken, shouldRefreshToken, autoRefreshToken } from '@/utils/auth'
import { GetUserPermission } from '@/api/users'
import tokenManager from '@/utils/tokenManager'
import { ElMessage, ElNotification } from 'element-plus'

const currentToken = ref('')
const remainingTime = ref(0)
const managerActive = ref(false)
const logs = ref([])
const updateTimer = ref(null)

const tokenStatus = computed(() => {
  if (!currentToken.value) {
    return { type: 'danger', text: '无Token' }
  }
  if (remainingTime.value <= 0) {
    return { type: 'danger', text: '已过期' }
  }
  if (remainingTime.value < 300) {
    return { type: 'warning', text: '即将过期' }
  }
  return { type: 'success', text: '正常' }
})

function addLog(message, type = 'info') {
  const time = new Date().toLocaleTimeString()
  logs.value.unshift({ time, message, type })
  if (logs.value.length > 50) {
    logs.value = logs.value.slice(0, 50)
  }
}

function formatTime(seconds) {
  if (seconds <= 0) return '已过期'
  
  const minutes = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  
  if (minutes > 0) {
    return `${minutes}分${secs}秒`
  }
  return `${secs}秒`
}

function parseTokenExpiry(token) {
  if (!token) return 0
  
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    const exp = payload.exp * 1000
    const now = Date.now()
    return Math.max(0, (exp - now) / 1000)
  } catch (error) {
    addLog('Token解析失败: ' + error.message, 'danger')
    return 0
  }
}

function updateTokenInfo() {
  currentToken.value = getToken() || ''
  remainingTime.value = parseTokenExpiry(currentToken.value)
  managerActive.value = tokenManager.isActive
}

function checkTokenStatus() {
  updateTokenInfo()
  const shouldRefresh = shouldRefreshToken()
  addLog(`Token检查完成，剩余时间: ${formatTime(remainingTime.value)}, 需要刷新: ${shouldRefresh}`, 'info')
}

async function manualRefresh() {
  addLog('开始手动刷新Token...', 'info')
  
  // 记录刷新前的token信息
  const oldToken = getToken()
  const oldExpiry = parseTokenExpiry(oldToken)
  addLog(`刷新前Token剩余时间: ${formatTime(oldExpiry)}`, 'info')
  
  try {
    const success = await autoRefreshToken(true) // 强制刷新
    if (success) {
      // 记录刷新后的token信息
      const newToken = getToken()
      const newExpiry = parseTokenExpiry(newToken)
      addLog(`刷新后Token剩余时间: ${formatTime(newExpiry)}`, 'info')
      addLog(`Token是否发生变化: ${oldToken !== newToken ? '是' : '否'}`, 'info')
      
      addLog('Token手动刷新成功', 'success')
      updateTokenInfo()
      ElMessage.success('Token刷新成功')
    } else {
      addLog('Token手动刷新失败', 'danger')
      ElMessage.error('Token刷新失败')
    }
  } catch (error) {
    addLog('Token手动刷新异常: ' + error.message, 'danger')
    ElMessage.error('Token刷新异常')
  }
}

async function testApiCall() {
  addLog('开始测试API调用...', 'info')
  try {
    await GetUserPermission()
    addLog('API调用成功', 'success')
    ElMessage.success('API调用成功')
    updateTokenInfo()
  } catch (error) {
    addLog('API调用失败: ' + error.message, 'danger')
    ElMessage.error('API调用失败')
  }
}

function startManager() {
  tokenManager.start()
  updateTokenInfo()
  addLog('Token管理器已启动', 'success')
}

function stopManager() {
  tokenManager.stop()
  updateTokenInfo()
  addLog('Token管理器已停止', 'warning')
}

onMounted(() => {
  updateTokenInfo()
  addLog('Token测试页面已加载', 'info')
  
  // 每秒更新一次显示
  updateTimer.value = setInterval(updateTokenInfo, 1000)
})

onUnmounted(() => {
  if (updateTimer.value) {
    clearInterval(updateTimer.value)
  }
})
</script>

<style scoped>
.token-test {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.token-text {
  word-break: break-all;
  font-family: monospace;
  font-size: 12px;
}

.actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.log-item {
  padding: 2px 0;
  border-bottom: 1px solid #f0f0f0;
}

.log-item:last-child {
  border-bottom: none;
}
</style>
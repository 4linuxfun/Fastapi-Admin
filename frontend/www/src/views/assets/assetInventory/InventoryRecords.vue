<template>
  <el-dialog v-model="dialogVisible" :title="`盘点记录 - ${batchInfo.batch_name}`" width="70%" :before-close="handleClose"
    destroy-on-close>
    <template #header>
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <span>盘点记录 - {{ batchInfo.batch_name }}</span>
        <el-tag :type="getStatusType(batchInfo.status)">{{ getStatusLabel(batchInfo.status) }}</el-tag>
      </div>
    </template>

    <!-- 批次统计信息 -->
    <el-row :gutter="20" style="margin: 20px 0;">
      <el-col :span="8">
        <el-card>
          <div class="stat-item">
            <div class="stat-number">{{ batchStats.total_assets }}</div>
            <div class="stat-label">总资产数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <div class="stat-item">
            <div class="stat-number" style="color: #67C23A;">{{ batchStats.completed_count }}</div>
            <div class="stat-label">已盘点</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <div class="stat-item">
            <div class="stat-number" style="color: #E6A23C;">{{ batchStats.pending_count }}</div>
            <div class="stat-label">未盘点</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 盘点进度 -->
    <el-row style="margin: 20px 0;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>盘点进度</span>
          </template>
          <el-progress :percentage="parseFloat(batchStats.completion_rate.toFixed(1))" :stroke-width="20" :text-inside="true"
            :color="getProgressColor(batchStats.completion_rate)" />
          <div style="margin-top: 10px; text-align: center;">
            完成率: {{ batchStats.completion_rate.toFixed(1) }}% ({{ batchStats.completed_count }}/{{
              batchStats.total_assets
            }})
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 盘点操作详情 -->
    <el-row :gutter="20" style="margin: 20px 0;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>盘点操作详情</span>
          </template>
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-number" style="color: #67C23A;">{{ actionStats.confirmed_in_place }}</div>
                <div class="stat-label">确认在位</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-number" style="color: #409EFF;">{{ actionStats.info_updated }}</div>
                <div class="stat-label">信息更新</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-number" style="color: #F56C6C;">{{ actionStats.exceptions }}</div>
                <div class="stat-label">异常处理</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-number" style="color: #E6A23C;">{{ actionStats.new_assets }}</div>
                <div class="stat-label">新增资产</div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>

    <!-- 盘点记录查询 -->
    <el-row>
      <el-form :model="search" :inline="true" ref="searchRef">
        <el-form-item label="资产编号" prop="asset_code">
          <el-input v-model="search.asset_code" clearable placeholder="请输入资产编号" />
        </el-form-item>
        <el-form-item label="盘点状态" prop="inventory_status">
          <el-select v-model="search.inventory_status" placeholder="请选择盘点状态" style="width: 150px;" clearable>
            <el-option label="未盘点" :value="0" />
            <el-option label="已盘点" :value="1" />
          </el-select>
        </el-form-item>
        <el-form-item label="操作类型" prop="action_type">
          <el-select v-model="search.action_type" placeholder="请选择操作类型" style="width: 150px;" clearable>
            <el-option label="确认在位" value="CONFIRM_IN_PLACE" />
            <el-option label="信息更新" value="INFO_UPDATE" />
            <el-option label="异常处理" value="EXCEPTION" />
            <el-option label="新增资产" value="NEW_ASSET" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch" :icon="Search" :loading="loading">搜索</el-button>
          <el-button @click="handleReset" :icon="RefreshRight" :loading="loading">重置</el-button>
          <el-button 
            type="success" 
            @click="handleAddAsset" 
            :icon="Plus"
            :disabled="!isInventoryAllowed"
            :title="isInventoryAllowed ? '新建资产' : '当前批次状态不允许新建资产'"
          >
            新建资产
          </el-button>
        </el-form-item>
      </el-form>
    </el-row>

    <!-- 盘点记录表格 -->
    <el-row>
      <el-col :span="24">
        <el-table :data="tableData" style="width: 100%" v-loading="loading" border>
          <el-table-column prop="asset_code" label="资产编号" width="150" />
          <el-table-column prop="name" label="资产名称" width="200" />
          <el-table-column prop="category_name" label="资产分类" width="120" />
          <el-table-column prop="location_name" label="位置" width="150" />
          <el-table-column prop="inventory_status" label="盘点状态" width="100">
            <template #default="scope">
              <el-tag :type="getInventoryStatusType(scope.row.inventory_status)">
                {{ getInventoryStatusLabel(scope.row.inventory_status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="latest_action_type" label="操作类型" width="120">
            <template #default="scope">
              <el-tag v-if="scope.row.latest_action_type" :type="getActionTypeColor(scope.row.latest_action_type)">
                {{ getActionTypeLabel(scope.row.latest_action_type) }}
              </el-tag>
              <span v-else style="color: #999;">-</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="scope">
              <el-button 
                type="primary" 
                size="small" 
                @click="handleInventory(scope.row)"
                :disabled="!isInventoryAllowed"
                :title="isInventoryAllowed ? '点击进行盘点' : '当前批次状态不允许盘点操作'"
              >
                盘点
              </el-button>
              <el-button type="info" size="small" @click="handleViewRecord(scope.row)">
                记录
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-col>
    </el-row>

    <!-- 分页 -->
    <el-row>
      <el-col :span="24">
        <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :page-sizes="[10, 20, 50, 100]"
          :small="false" :disabled="false" :background="true" layout="total, sizes, prev, pager, next, jumper"
          :total="total" @size-change="freshCurrentPage" @current-change="freshCurrentPage" />
      </el-col>
    </el-row>

    <!-- 盘点对话框 -->
    <InventoryDialog 
      v-model:visible="inventoryDialogVisible" 
      :asset-data="currentAsset" 
      :current-batch="batchId"
      @confirm="handleInventoryConfirm"
    />

    <!-- 新建资产对话框 -->
    <AddAsset ref="addAssetRef" @success="handleAddAssetSuccess" />
    
    <!-- 资产日志对话框 -->
    <AssetLogs ref="assetLogsRef" />
    
    <!-- 盘点日志对话框 -->
    <InventoryLogs ref="inventoryLogsRef" />
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch, nextTick, computed } from 'vue'
import { Search, RefreshRight, Plus } from '@element-plus/icons-vue'
import usePagination from '@/composables/usePagination'
import { GetInventoryBatchSummary, GetBatchInventoryRecords } from '@/api/assets'
import { ElMessage } from 'element-plus'
import InventoryDialog from './InventoryDialog.vue'
import AddAsset from '../assetsList/AddAsset.vue'
import AssetLogs from '../assetsList/assetLogs.vue'
import InventoryLogs from './InventoryLogs.vue'

defineOptions({
  name: '盘点记录对话框'
})

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  batchData: {
    type: Object,
    default: () => ({})
  }
})

// Emits
const emit = defineEmits(['update:visible'])

// 对话框显示状态
const dialogVisible = ref(false)

// 获取批次ID
const batchId = ref(null)
const batchInfo = ref({
  batch_name: '',
  status: '',
  start_date: '',
  end_date: ''
})

// 批次统计信息
const batchStats = ref({
  total_assets: 0,
  completed_count: 0,
  pending_count: 0,
  exception_count: 0,
  completion_rate: 0
})

// 操作类型统计信息
const actionStats = ref({
  confirmed_in_place: 0,
  info_updated: 0,
  exceptions: 0,
  new_assets: 0
})

// 监听对话框显示状态
watch(() => props.visible, (newVal) => {
  dialogVisible.value = newVal
  if (newVal && props.batchData) {
    initializeData()
  }
})

// 监听对话框内部状态变化
watch(dialogVisible, (newVal) => {
  emit('update:visible', newVal)
})

// 初始化数据
const initializeData = () => {
  batchId.value = props.batchData.id
  // 更新搜索表单中的last_inventory_batch_id
  search.last_inventory_batch_id = props.batchData.id
  batchInfo.value = {
    batch_name: props.batchData.batch_name || '',
    status: props.batchData.status || '',
    start_date: props.batchData.start_date || '',
    end_date: props.batchData.end_date || ''
  }
  nextTick(() => {
    loadBatchInfo()
  })
}

// 搜索表单
const searchForm = reactive({
  last_inventory_batch_id: batchId.value,
  asset_code: null,
  inventory_status: null,
  action_type: null
})

const searchRef = ref()

// 分页相关
const {
  search,
  tableData,
  currentPage,
  pageSize,
  total,
  loading,
  freshCurrentPage,
  handleSearch
} = usePagination('/api/assets/search/inventory-assets', searchForm, 'desc')

// 状态相关方法
const statusData = [
  { label: '进行中', value: 'active', type: 'primary' },
  { label: '已完成', value: 'completed', type: 'success' },
  { label: '已关闭', value: 'closed', type: 'warning' }
]

function getStatusType(status) {
  const statusItem = statusData.find(item => item.value === status)
  return statusItem ? statusItem.type : 'info'
}

function getStatusLabel(status) {
  const statusItem = statusData.find(item => item.value === status)
  return statusItem ? statusItem.label : status
}

function getInventoryStatusType(status) {
  const statusMap = {
    0: 'warning',  // 未盘点
    1: 'success',  // 已盘点
    2: 'success'   // 异常（现在也归类为已盘点）
  }
  return statusMap[status] || 'info'
}

function getInventoryStatusLabel(status) {
  const statusMap = {
    0: '未盘点',
    1: '已盘点',
    2: '已盘点'  // 异常状态也显示为已盘点
  }
  return statusMap[status] || '未知'
}

function getActionTypeColor(actionType) {
  const colorMap = {
    'CONFIRM_IN_PLACE': 'success',
    'INFO_UPDATE': 'primary',
    'EXCEPTION': 'danger',
    'NEW_ASSET': 'warning'
  }
  return colorMap[actionType] || 'info'
}

function getActionTypeLabel(actionType) {
  const labelMap = {
    'CONFIRM_IN_PLACE': '确认在位',
    'INFO_UPDATE': '信息更新',
    'EXCEPTION': '异常处理',
    'NEW_ASSET': '新增资产'
  }
  return labelMap[actionType] || actionType
}

function getProgressColor(percentage) {
  if (percentage < 30) return '#F56C6C'
  if (percentage < 70) return '#E6A23C'
  return '#67C23A'
}

// 格式化日期时间
function formatDateTime(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 对话框关闭处理
const handleClose = () => {
  dialogVisible.value = false
}

// 重置搜索表单
function handleReset() {
  searchRef.value.resetFields()
  search.last_inventory_batch_id = batchId.value // 保持批次ID
  search.asset_code = null
  search.inventory_status = null
  search.action_type = null
  handleSearch()
}

// 盘点对话框状态
const inventoryDialogVisible = ref(false)
const currentAsset = ref(null)



// 新建资产对话框引用
const addAssetRef = ref(null)

// 资产日志对话框引用
const assetLogsRef = ref(null)

// 盘点日志对话框引用
const inventoryLogsRef = ref(null)

// 判断是否允许盘点操作
const isInventoryAllowed = computed(() => {
  return batchInfo.value.status === 'active'
})

// 处理盘点操作
function handleInventory(row) {
  if (!isInventoryAllowed.value) {
    ElMessage.warning('当前批次状态不允许盘点操作')
    return
  }
  currentAsset.value = row
  inventoryDialogVisible.value = true
  console.log('打开盘点对话框:', row)
}

// 处理查看记录操作
function handleViewRecord(row) {
  if (inventoryLogsRef.value) {
    inventoryLogsRef.value.show(row.id, batchId.value)
  }
  console.log('打开盘点日志对话框:', row, '批次ID:', batchId.value)
}

// 处理盘点确认
function handleInventoryConfirm(inventoryData) {
  console.log('盘点确认数据:', inventoryData)
  // 这里可以调用API提交盘点数据
  // 提交成功后刷新列表和统计数据
  handleSearch()
  loadBatchInfo()
  ElMessage.success('盘点提交成功')
}

// 关闭盘点对话框
function closeInventoryDialog() {
  inventoryDialogVisible.value = false
  currentAsset.value = null
}



// 处理新建资产
function handleAddAsset() {
  if (!isInventoryAllowed.value) {
    ElMessage.warning('当前批次状态不允许新建资产')
    return
  }
  if (addAssetRef.value) {
    addAssetRef.value.addWithBatch(batchId.value)
  }
}

// 新建资产成功回调
function handleAddAssetSuccess() {
  // 刷新列表和统计数据
  handleSearch()
  loadBatchInfo()
  ElMessage.success('资产新建成功')
}

// 加载批次信息和统计数据
async function loadBatchInfo() {
  try {
    console.log('开始获取批次信息，批次ID:', batchId.value)
    // 调用获取批次详情和统计数据的API
    const response = await GetInventoryBatchSummary(batchId.value)
    console.log('API响应:', response)

    if (response && response.batch_info) {
      // 解析批次基本信息
      batchInfo.value = {
        batch_name: response.batch_info.batch_name || '',
        status: response.batch_info.status || '',
        start_date: response.batch_info.start_date || '',
        end_date: response.batch_info.end_date || ''
      }
      console.log('批次信息解析成功:', batchInfo.value)

      // 解析统计数据
      if (response.statistics) {
        const stats = response.statistics
        console.log('统计数据:', stats)

        // 获取统计数据，与App端保持一致的命名
        const checked = stats.scanned_assets || 0  // 已盘点数量
        const unchecked = stats.unscanned_assets || 0  // 未盘点数量
        const total = checked + unchecked  // 总资产数

        // 计算完成率 - 与App端保持一致的计算方式
        const completionRate = total === 0 ? 0 : (checked / total) * 100

        batchStats.value = {
          total_assets: total, // 总资产数
          completed_count: checked, // 已盘点数量
          pending_count: unchecked, // 未盘点数量
          completion_rate: completionRate
        }

        // 更新操作类型统计信息
        actionStats.value = {
          confirmed_in_place: stats.action_breakdown?.confirmed_in_place || 0,
          info_updated: stats.action_breakdown?.info_updated || 0,
          exceptions: stats.action_breakdown?.exceptions || 0,
          new_assets: stats.action_breakdown?.new_assets || 0
        }

        console.log('统计数据解析成功:', batchStats.value, actionStats.value)
      } else {
        console.warn('响应中缺少statistics字段')
        // 如果没有统计数据，使用默认值
        batchStats.value = {
          total_assets: 0,
          completed_count: 0,
          pending_count: 0,
          completion_rate: 0
        }
        actionStats.value = {
          confirmed_in_place: 0,
          info_updated: 0,
          exceptions: 0,
          new_assets: 0
        }
      }
    } else {
      console.error('API响应格式错误或缺少batch_info:', response)
      ElMessage.error('获取批次信息失败：数据格式错误')
      // 设置默认统计值
      batchInfo.value = {
        batch_name: '',
        status: '',
        start_date: '',
        end_date: ''
      }
      batchStats.value = {
        total_assets: 0,
        completed_count: 0,
        pending_count: 0,
        completion_rate: 0
      }
      actionStats.value = {
        confirmed_in_place: 0,
        info_updated: 0,
        exceptions: 0,
        new_assets: 0
      }
    }
    // 加载完批次信息后，执行搜索
    handleSearch()
  } catch (error) {
    console.error('获取批次信息失败:', error)
    const errorMsg = error.response?.data?.message || error.message || '获取批次信息失败'
    ElMessage.error(errorMsg)
    // 设置默认统计值
    batchInfo.value = {
      batch_name: '',
      status: '',
      start_date: '',
      end_date: ''
    }
    batchStats.value = {
      total_assets: 0,
      completed_count: 0,
      pending_count: 0,
      completion_rate: 0
    }
    actionStats.value = {
      confirmed_in_place: 0,
      info_updated: 0,
      exceptions: 0,
      new_assets: 0
    }
  }
}
</script>

<style scoped>
.el-row {
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
  padding: 10px;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #666;
  font-weight: normal;
}

.el-card {
  height: 100%;
}
</style>
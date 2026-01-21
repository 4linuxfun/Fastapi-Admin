<template>
  <el-dialog v-model="visible" title="盘点历史记录" width="60%" :close-on-click-modal="false">
    <el-form inline :model="formData">

      <el-form-item label="开始时间">
        <el-date-picker v-model="formData.start" type="date" placeholder="选择开始日期" value-format="YYYY-MM-DD"
          style="width: 200px;" />
      </el-form-item>
      <el-form-item label="结束时间">
        <el-date-picker v-model="formData.end" type="date" placeholder="选择结束日期" value-format="YYYY-MM-DD"
          style="width: 200px;" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSearch" :loading="loading">查询</el-button>
        <el-button @click="handleReset">重置</el-button>
      </el-form-item>
    </el-form>

    <div v-if="inventoryLogs.length === 0 && !loading" style="text-align: center; padding: 40px; color: #999;">
      暂无盘点记录
    </div>

    <el-timeline v-loading="loading">
      <el-timeline-item v-for="(log, index) in inventoryLogs" :key="index" :timestamp="log.scanned_at" placement="top"
        center>
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-weight: bold;">{{ getActionTypeLabel(log.action_type) }}</span>
              <div>
                <el-tag :type="getActionTypeColor(log.action_type)" size="small">
                  {{ getActionTypeLabel(log.action_type) }}
                </el-tag>
                <el-tag v-if="log.batch_name" type="info" size="small" style="margin-left: 8px;">
                  {{ log.batch_name }}
                </el-tag>
              </div>
            </div>
          </template>

          <!-- 确认在位 -->
          <el-descriptions v-if="log.action_type === 'CONFIRM_IN_PLACE'" :column="2">
            <el-descriptions-item label="资产编号">{{ log.asset_code || '-' }}</el-descriptions-item>
            <el-descriptions-item label="资产名称">{{ log.asset_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="资产分类">{{ log.asset?.category_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="实际位置">{{ log.actual_location_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="盘点人">{{ log.scanned_by_user_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="盘点时间">{{ log.scanned_at || '-' }}</el-descriptions-item>
            <el-descriptions-item label="备注" :span="2">{{ log.remarks || '无' }}</el-descriptions-item>
            <el-descriptions-item label="盘点图片" :span="2">
              <template v-if="log.photo_urls && log.photo_urls.length > 0">
                <el-image v-for="(image, imgIndex) in log.photo_urls" :key="imgIndex" :src="image"
                  :preview-src-list="log.photo_urls" style="width: 100px; height: 100px; margin-right: 8px;"
                  fit="cover" />
              </template>
              <template v-else>无</template>
            </el-descriptions-item>
          </el-descriptions>

          <!-- 信息更新 -->
          <el-descriptions v-else-if="log.action_type === 'INFO_UPDATE'" :column="2">
            <el-descriptions-item label="资产编号">{{ log.asset_code || '-' }}</el-descriptions-item>
            <el-descriptions-item label="资产名称">{{ log.asset_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="资产分类">{{ log.asset?.category_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="实际位置">{{ log.actual_location_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="盘点人">{{ log.scanned_by_user_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="盘点时间">{{ log.scanned_at || '-' }}</el-descriptions-item>
            <el-descriptions-item label="更新详情" :span="2">
              <div v-if="log.details">
                <div v-for="(value, key) in parseDetails(log.details)" :key="key" style="margin-bottom: 8px;">
                  <div style="display: flex; align-items: center; gap: 8px;">
                    <el-tag size="small" type="info">{{ getDetailLabel(key) }}</el-tag>
                    <span v-if="value.from && value.to">
                      <el-tag size="small" type="warning">{{ value.from || '空' }}</el-tag>
                      <el-icon style="margin: 0 4px;"><Right /></el-icon>
                      <el-tag size="small" type="success">{{ value.to || '空' }}</el-tag>
                    </span>
                    <span v-else-if="value.to">
                      <span style="color: #909399;">设置为：</span>
                      <el-tag size="small" type="success">{{ value.to }}</el-tag>
                    </span>
                    <span v-else>{{ value }}</span>
                  </div>
                </div>
              </div>
              <span v-else>无更新详情</span>
            </el-descriptions-item>
            <el-descriptions-item label="备注" :span="2">{{ log.remarks || '无' }}</el-descriptions-item>
            <el-descriptions-item label="盘点图片" :span="2">
              <template v-if="log.photo_urls && log.photo_urls.length > 0">
                <el-image v-for="(image, imgIndex) in log.photo_urls" :key="imgIndex" :src="image"
                  :preview-src-list="log.photo_urls" style="width: 100px; height: 100px; margin-right: 8px;"
                  fit="cover" />
              </template>
              <template v-else>无</template>
            </el-descriptions-item>
          </el-descriptions>

          <!-- 异常处理 -->
          <el-descriptions v-else-if="log.action_type === 'EXCEPTION'" :column="2">
            <el-descriptions-item label="资产编号">{{ log.asset_code || '-' }}</el-descriptions-item>
            <el-descriptions-item label="资产名称">{{ log.asset_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="盘点人">{{ log.scanned_by_user_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="盘点时间">{{ log.scanned_at || '-' }}</el-descriptions-item>
            <el-descriptions-item label="异常详情" :span="2">
              <div v-if="log.details">
                <div v-for="(value, key) in parseDetails(log.details)" :key="key" style="margin-bottom: 8px;">
                  <div v-if="key === 'description'" style="margin-bottom: 8px;">
                    <el-tag size="small" type="info">异常描述</el-tag>
                    <span style="margin-left: 8px;">{{ value }}</span>
                  </div>
                  <div v-else-if="key === 'severity'" style="margin-bottom: 8px;">
                    <el-tag size="small" type="info">严重程度</el-tag>
                    <el-tag 
                      size="small" 
                      :type="value === 'high' ? 'danger' : 'warning'"
                      style="margin-left: 8px;"
                    >
                      {{ value === 'high' ? '高' : '中' }}
                    </el-tag>
                  </div>
                </div>
              </div>
              <div v-else>
                <el-tag type="danger" size="small">{{ getExceptionRemarks(log) }}</el-tag>
              </div>
            </el-descriptions-item>
            <el-descriptions-item label="盘点图片" :span="2">
              <template v-if="log.photo_urls && log.photo_urls.length > 0">
                <el-image v-for="(image, imgIndex) in log.photo_urls" :key="imgIndex" :src="image"
                  :preview-src-list="log.photo_urls" style="width: 100px; height: 100px; margin-right: 8px;"
                  fit="cover" />
              </template>
              <template v-else>无</template>
            </el-descriptions-item>
          </el-descriptions>

          <!-- 新增资产 -->
          <el-descriptions v-else-if="log.action_type === 'NEW_ASSET'" :column="2">
            <el-descriptions-item label="资产编号">{{ log.asset_code || '-' }}</el-descriptions-item>
            <el-descriptions-item label="资产名称">{{ log.asset_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="资产品牌">{{ log.asset?.brand || '-' }}</el-descriptions-item>
            <el-descriptions-item label="资产型号">{{ log.asset?.model || '-' }}</el-descriptions-item>
            <el-descriptions-item label="序列号">{{ log.asset?.serial_number || '-' }}</el-descriptions-item>
            <el-descriptions-item label="盘点人">{{ log.scanned_by_user_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="盘点时间" :span="2">{{ log.scanned_at || '-' }}</el-descriptions-item>
            <el-descriptions-item label="初始设置" :span="2">
              <div v-if="log.details">
                <div v-for="(value, key) in parseDetails(log.details)" :key="key" style="margin-bottom: 8px;">
                  <div style="display: flex; align-items: center; gap: 8px;">
                    <el-tag size="small" type="info">{{ getDetailLabel(key) }}</el-tag>
                    <span v-if="value.to">
                      <el-tag size="small" type="success">{{ value.to }}</el-tag>
                    </span>
                    <span v-else>{{ value }}</span>
                  </div>
                </div>
              </div>
              <span v-else>无初始设置信息</span>
            </el-descriptions-item>
            <el-descriptions-item label="备注" :span="2">{{ log.remarks || '无' }}</el-descriptions-item>
            <el-descriptions-item label="盘点图片" :span="2">
              <template v-if="log.photo_urls && log.photo_urls.length > 0">
                <el-image v-for="(image, imgIndex) in log.photo_urls" :key="imgIndex" :src="image"
                  :preview-src-list="log.photo_urls" style="width: 100px; height: 100px; margin-right: 8px;"
                  fit="cover" />
              </template>
              <template v-else>无</template>
            </el-descriptions-item>
          </el-descriptions>

          <!-- 其他类型 -->
          <el-descriptions v-else :column="2">
            <el-descriptions-item label="资产编号">{{ log.asset_code || '-' }}</el-descriptions-item>
            <el-descriptions-item label="资产名称">{{ log.asset_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="盘点人">{{ log.scanned_by_user_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="盘点时间">{{ log.scanned_at || '-' }}</el-descriptions-item>
            <el-descriptions-item label="详情" :span="2">{{ log.details || '无' }}</el-descriptions-item>
            <el-descriptions-item label="备注" :span="2">{{ log.remarks || '无' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-timeline-item>
    </el-timeline>
  </el-dialog>
</template>

<script setup>
import { ref, reactive } from 'vue'
import dayjs from 'dayjs'
import { ElMessage } from 'element-plus'
import { Right } from '@element-plus/icons-vue'
import { GetAssetInventoryLogs } from '@/api/assets'

defineOptions({
  name: '盘点历史记录'
})

const visible = ref(false)
const assetId = ref(null)
const loading = ref(false)
const inventoryLogs = ref([])

const formData = reactive({
  batch_id: '',
  start: '',
  end: ''
})

// 操作类型标签映射
function getActionTypeLabel(actionType) {
  const labelMap = {
    'CONFIRM_IN_PLACE': '确认在位',
    'INFO_UPDATE': '信息更新',
    'EXCEPTION': '异常处理',
    'NEW_ASSET': '新增资产'
  }
  return labelMap[actionType] || actionType
}

// 操作类型颜色映射
function getActionTypeColor(actionType) {
  const colorMap = {
    'CONFIRM_IN_PLACE': 'success',
    'INFO_UPDATE': 'primary',
    'EXCEPTION': 'danger',
    'NEW_ASSET': 'warning'
  }
  return colorMap[actionType] || 'info'
}

// 解析详情字段
function parseDetails(details) {
  if (!details) return {}

  try {
    if (typeof details === 'string') {
      return JSON.parse(details)
    }
    return details
  } catch (error) {
    console.error('解析详情字段失败:', error)
    return {}
  }
}

// 详情字段标签映射
function getDetailLabel(key) {
  const labelMap = {
    'location': '位置',
    'owner': '使用人',
    'status': '状态',
    'category': '资产分类',
    'remarks': '备注',
    'name': '名称',
    'brand': '品牌',
    'model': '型号',
    'serial_number': '序列号',
    'purchase_date': '购买日期',
    'description': '异常描述',
    'severity': '严重程度'
  }
  return labelMap[key] || key
}

// 获取异常原因
function getExceptionRemarks(log) {
  // 优先从details字段中解析description
  if (log.details) {
    try {
      const details = typeof log.details === 'string' ? JSON.parse(log.details) : log.details
      if (details.description) {
        return details.description
      }
    } catch (error) {
      console.error('解析异常详情失败:', error)
    }
  }

  // 如果details中没有description，则使用log.remarks
  return log.remarks || '未说明异常原因'
}

// 查询盘点日志
async function handleSearch() {
  if (!assetId.value) {
    ElMessage.warning('资产ID不能为空')
    return
  }

  loading.value = true
  try {
    const params = {
      batch_id: formData.batch_id || undefined,
      start_date: formData.start || undefined,
      end_date: formData.end || undefined
    }

    console.log('查询参数:', params)

    const response = await GetAssetInventoryLogs(assetId.value, params)

    if (response) {
      inventoryLogs.value = response.map(log => {
        // 格式化时间
        if (log.scanned_at) {
          log.scanned_at = dayjs(log.scanned_at).format('YYYY-MM-DD HH:mm:ss')
        }

        // 解析图片URL
        if (log.photo_urls && typeof log.photo_urls === 'string') {
          try {
            log.photo_urls = JSON.parse(log.photo_urls)
          } catch (error) {
            console.error('解析图片URL失败:', error)
            log.photo_urls = []
          }
        }

        return log
      })

      if (inventoryLogs.value.length === 0) {
        ElMessage.info('未找到相关盘点记录')
      }
    } else {
      inventoryLogs.value = []
      ElMessage.info('未找到相关盘点记录')
    }
  } catch (error) {
    console.error('获取盘点日志失败:', error)
    ElMessage.error('获取盘点日志失败')
    inventoryLogs.value = []
  } finally {
    loading.value = false
  }
}

// 重置查询条件
function handleReset() {
  formData.batch_id = ''
  formData.start = dayjs().subtract(1, 'month').format('YYYY-MM-DD')
  formData.end = dayjs().format('YYYY-MM-DD')
  handleSearch()
}

// 显示对话框
async function show(id, batchId = null) {
  visible.value = true
  assetId.value = id
  inventoryLogs.value = []

  // 设置默认时间范围（最近一个月）
  formData.batch_id = batchId || ''
  formData.start = dayjs().subtract(1, 'month').format('YYYY-MM-DD')
  formData.end = dayjs().format('YYYY-MM-DD')

  await handleSearch()
}

defineExpose({
  show
})
</script>

<style scoped>
.el-timeline {
  margin-top: 20px;
}

.el-card {
  margin-bottom: 16px;
}

.el-descriptions {
  margin-top: 16px;
}

.el-image {
  border-radius: 4px;
  border: 1px solid #dcdfe6;
}
</style>
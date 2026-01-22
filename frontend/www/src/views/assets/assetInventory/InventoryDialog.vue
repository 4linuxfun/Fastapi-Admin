<template>
  <el-dialog
    v-model="dialogVisible"
    title="盘点确认"
    width="600px"
    :before-close="handleClose"
    destroy-on-close
  >
    <template #header>
      <div class="dialog-header">
        <span>盘点确认</span>
      </div>
    </template>

    <div v-if="assetData" class="inventory-content">
      <!-- 资产基本信息 -->
      <div class="asset-info">
        <div class="asset-title">
          <h3>{{ assetData.name }}</h3>
          <span class="asset-code">{{ assetData.asset_code }}</span>
          <el-tag type="success" size="small">在库</el-tag>
        </div>
        
        <el-row :gutter="20" class="asset-details">
          <el-col :span="12">
            <div class="info-item">
              <span class="label">资产编码</span>
              <span class="value">{{ assetData.asset_code }}</span>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="info-item">
              <span class="label">资产分类</span>
              <span class="value">{{ assetData.category_name }}</span>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="info-item">
              <span class="label">当前状态</span>
              <span class="value">在库</span>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="info-item">
              <span class="label">当前位置</span>
              <span class="value">{{ assetData.location_name }}</span>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="info-item">
              <span class="label">使用人</span>
              <span class="value">{{ assetData.owner || '未设置' }}</span>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="info-item">
              <span class="label">型号</span>
              <span class="value">{{ assetData.model }}</span>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="info-item">
              <span class="label">序列号</span>
              <span class="value">{{ assetData.serial_number }}</span>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 盘点信息表单 -->
      <div class="inventory-form">
        <div class="form-header">
          <h4>盘点信息</h4>
          <div class="action-type">
            <span>操作类型：</span>
            <el-tag :type="actionTypeConfig.type" :class="actionTypeConfig.class" size="small">
              {{ actionTypeConfig.text }}
            </el-tag>
          </div>
        </div>
        
        <el-form :model="inventoryForm" :rules="rules" ref="inventoryFormRef" label-width="100px">
          <el-form-item label="实际状态" prop="actual_status">
            <el-select v-model="inventoryForm.actual_status" placeholder="请选择实际状态" style="width: 100%">
              <el-option label="在库" value="0" />
              <el-option label="使用中" value="1" />
              <el-option label="维修中" value="2" />
              <el-option label="报废" value="3" />
              <el-option label="其他" value="4" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="实际位置" prop="actual_location_id">
            <el-tree-select v-model="inventoryForm.actual_location_id" :data="locationData" :render-after-expand="false"
              :props="{ label: 'name' }" value-key="id" check-strictly placeholder="请选择实际位置" />
          </el-form-item>
          
          <el-form-item label="实际使用人" prop="actual_owner">
            <el-input 
              v-model="inventoryForm.actual_owner" 
              placeholder="请输入实际使用人" 
            />
          </el-form-item>
          
          <el-form-item label="异常情况" prop="exception_type">
            <el-select v-model="inventoryForm.exception_type" placeholder="请选择异常情况" style="width: 100%" @change="handleExceptionChange">
              <el-option
                v-for="item in exceptionTypeOptions"
                :key="item.value"
                :label="item.text"
                :value="item.value"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="盘点备注" prop="remarks">
            <el-input 
              v-model="inventoryForm.remarks" 
              type="textarea" 
              :rows="3" 
              placeholder="请输入盘点备注" 
            />
          </el-form-item>
        </el-form>
      </div>

      <!-- 盘点图片 -->
      <div class="inventory-images">
        <h4>盘点图片</h4>
        <div class="upload-area">
          <el-upload
            ref="uploadRef"
            class="image-uploader"
            action="#"
            :file-list="uploadFiles"
            :before-upload="beforeImageUpload"
            :on-change="handleFileChange"
            :auto-upload="false"
            multiple
            accept="image/*"
          >
            <div class="upload-placeholder">
              <el-icon class="upload-icon"><Camera /></el-icon>
              <div class="upload-text">点击上传图片</div>
            </div>
          </el-upload>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose" size="large">取消</el-button>
        <el-button type="primary" @click="handleConfirm" size="large" :loading="loading">
          确认盘点
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch, onMounted, computed } from 'vue'
import { Camera } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { GetAssetLocationTree, CreateInventoryRecord } from '@/api/assets'

defineOptions({
  name: '盘点对话框'
})

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  assetData: {
    type: Object,
    default: () => ({})
  },
  currentBatch: {
    type: Number,
    required: true
  }
})

// Emits
const emit = defineEmits(['update:visible', 'confirm'])

// 对话框显示状态
const dialogVisible = ref(false)
const loading = ref(false)

// 表单引用
const inventoryFormRef = ref()

// 盘点表单数据
const inventoryForm = reactive({
  actual_status: '',
  actual_location_id: null,
  actual_owner: '',
  exception_status: 'normal',
  exception_type: 'normal',
  remarks: ''
})

// 文件上传相关
const uploadFiles = ref([])

const locationData = ref([])

// 异常状态选项
const exceptionStatusOptions = [
  { value: 'normal', label: '正常' },
  { value: 'abnormal', label: '异常' }
]

// 异常类型选项
const exceptionTypeOptions = [
  { value: 'normal', text: '正常' },
  { value: 'not_found', text: '资产无法找到' },
  { value: 'damaged', text: '资产损坏' },
  { value: 'label_unclear', text: '标识模糊' },
  { value: 'location_mismatch', text: '位置不符' },
  { value: 'other_exception', text: '其他异常' }
]

// 表单验证规则
const rules = {
  actual_status: [
    { required: true, message: '请选择实际状态', trigger: 'change' }
  ],
  actual_location_id: [
    { required: true, message: '请选择实际位置', trigger: 'change' }
  ]
}

// 监听对话框显示状态
watch(() => props.visible, (newVal) => {
  dialogVisible.value = newVal
  if (newVal && props.assetData) {
    initializeForm()
  }
})

// 监听对话框内部状态变化
watch(dialogVisible, (newVal) => {
  emit('update:visible', newVal)
})

// 初始化表单数据
const initializeForm = () => {
  // 根据资产当前信息预填表单
  inventoryForm.actual_status = props.assetData.status || '0'
  inventoryForm.actual_location_id = props.assetData.location_id || null
  inventoryForm.actual_owner = props.assetData.owner || ''
  inventoryForm.exception_status = 'normal'
  inventoryForm.exception_type = 'normal'
  inventoryForm.remarks = ''
  // 清空文件列表
  uploadFiles.value = []
}

// 加载位置数据
const loadLocationData = async () => {
  try {
    locationData.value = await GetAssetLocationTree()
  } catch (error) {
    console.error('获取位置数据失败:', error)
    ElMessage.error('获取位置数据失败')
  }
}

// 动态操作类型配置
const actionTypeConfig = computed(() => {
  // 检查是否有异常
  if (inventoryForm.exception_type !== 'normal') {
    return {
      text: '异常处理',
      type: 'danger',
      class: 'action-tag-exception'
    }
  }
  
  // 检查是否有信息变更（位置、使用人或状态发生变化）
  const hasLocationChange = inventoryForm.actual_location_id && 
    inventoryForm.actual_location_id !== props.assetData.location_id
  const hasUserChange = inventoryForm.actual_owner && 
    inventoryForm.actual_owner !== props.assetData.owner
  const hasStatusChange = inventoryForm.actual_status && 
    inventoryForm.actual_status !== (props.assetData.status || '0')
  
  if (hasLocationChange || hasUserChange || hasStatusChange) {
    return {
      text: '信息更新',
      type: 'warning',
      class: 'action-tag-update'
    }
  }
  
  // 默认确认在位
  return {
    text: '确认在位',
    type: 'success',
    class: 'action-tag-confirm'
  }
})

// 组件挂载时加载位置数据
onMounted(() => {
  loadLocationData()
})

// 图片上传相关
const uploadRef = ref()

const beforeImageUpload = (file) => {
  const isJPG = file.type === 'image/jpeg' || file.type === 'image/png'
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isJPG) {
    ElMessage.error('上传图片只能是 JPG/PNG 格式!')
  }
  if (!isLt2M) {
    ElMessage.error('上传图片大小不能超过 2MB!')
  }
  return isJPG && isLt2M
}

const handleFileChange = (file, fileList) => {
  uploadFiles.value = fileList
}

// 对话框关闭处理
const handleClose = () => {
  dialogVisible.value = false
}

// 处理异常情况变化
const handleExceptionChange = (value) => {
  if (value !== 'normal') {
    // 选择异常时，自动设置盘点状态为异常
    inventoryForm.exception_status = 'abnormal'
    
    const selectedOption = exceptionTypeOptions.find(option => option.value === value)
    if (selectedOption) {
      // 在备注中自动带出异常内容
      inventoryForm.remarks = selectedOption.text
    }
  } else {
    // 选择正常时，设置盘点状态为正常，清空备注
    inventoryForm.exception_status = 'normal'
    inventoryForm.remarks = ''
  }
}

// 重置表单
const resetForm = () => {
  inventoryForm.actual_status = ''
  inventoryForm.actual_location_id = null
  inventoryForm.actual_owner = ''
  inventoryForm.exception_status = 'normal'
  inventoryForm.exception_type = 'normal'
  inventoryForm.remarks = ''
  uploadFiles.value = []
  if (inventoryFormRef.value) {
    inventoryFormRef.value.clearValidate()
  }
}

// 确认盘点
const handleConfirm = async () => {
  try {
    // 表单验证
    await inventoryFormRef.value.validate()
    
    loading.value = true
    
    // 根据实际情况确定操作类型
    let actionType = 'CONFIRM_IN_PLACE' // 默认确认在位
    
    // 检查是否有异常
    if (inventoryForm.exception_type !== 'normal') {
      actionType = 'EXCEPTION'
    } else {
      // 检查是否有信息变更（位置、使用人或状态发生变化）
      const hasLocationChange = inventoryForm.actual_location_id && 
        inventoryForm.actual_location_id !== props.assetData.location_id
      const hasUserChange = inventoryForm.actual_owner && 
        inventoryForm.actual_owner !== props.assetData.owner
      const hasStatusChange = inventoryForm.actual_status && 
        inventoryForm.actual_status !== (props.assetData.status || '0')
      
      if (hasLocationChange || hasUserChange || hasStatusChange) {
        actionType = 'INFO_UPDATE'
      }
    }
    
    // 构建FormData对象
    const formData = new FormData()
    
    // 添加基本字段
    formData.append('asset_id', props.assetData.id)
    formData.append('batch_id', props.currentBatch)
    formData.append('action_type', actionType)
    formData.append('actual_status', inventoryForm.actual_status)
    formData.append('actual_location_id', inventoryForm.actual_location_id)
    formData.append('actual_owner', inventoryForm.actual_owner)
    formData.append('remarks', inventoryForm.remarks)
    
    // 添加图片文件
    uploadFiles.value.forEach((file) => {
      if (file.raw) {
        formData.append('files', file.raw)
      }
    })
    
    console.log('提交盘点数据:', {
      asset_id: props.assetData.id,
      batch_id: props.currentBatch,
      action_type: actionType,
      actual_status: inventoryForm.actual_status,
      actual_location_id: inventoryForm.actual_location_id,
      actual_owner: inventoryForm.actual_owner,
      remarks: inventoryForm.remarks,
      files: uploadFiles.value.length
    })
    
    // 调用盘点API
    await CreateInventoryRecord(formData)
    
    ElMessage.success('盘点提交成功')
    emit('confirm', {
      asset_id: props.assetData.id,
      batch_id: props.currentBatch,
      action_type: actionType,
      actual_status: inventoryForm.actual_status,
      actual_location_id: inventoryForm.actual_location_id,
      actual_owner: inventoryForm.actual_owner,
      remarks: inventoryForm.remarks
    })
    resetForm()
    handleClose()
    
  } catch (error) {
    console.error('盘点提交失败:', error)
    if (error !== false) { // 不是表单验证错误
      ElMessage.error('盘点提交失败，请重试')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.dialog-header {
  display: flex;
  align-items: center;
  font-size: 16px;
  font-weight: 500;
}

.inventory-content {
  max-height: 70vh;
  overflow-y: auto;
}

.asset-info {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.asset-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.asset-title h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
}

.asset-code {
  color: #666;
  font-size: 14px;
}

.asset-details {
  margin-top: 16px;
}

.info-item {
  display: flex;
  margin-bottom: 8px;
}

.info-item .label {
  width: 80px;
  color: #666;
  font-size: 14px;
}

.info-item .value {
  flex: 1;
  color: #333;
  font-size: 14px;
}

.inventory-form {
  margin-bottom: 20px;
}

.inventory-form h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 500;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.action-type {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.action-tag-confirm {
  background: linear-gradient(135deg, #67c23a, #85ce61);
  border: none;
  color: white;
  font-weight: 500;
  box-shadow: 0 2px 4px rgba(103, 194, 58, 0.3);
}

.action-tag-update {
  background: linear-gradient(135deg, #e6a23c, #f0c78a);
  border: none;
  color: white;
  font-weight: 500;
  box-shadow: 0 2px 4px rgba(230, 162, 60, 0.3);
}

.action-tag-exception {
  background: linear-gradient(135deg, #f56c6c, #f89898);
  border: none;
  color: white;
  font-weight: 500;
  box-shadow: 0 2px 4px rgba(245, 108, 108, 0.3);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 2px 4px rgba(245, 108, 108, 0.3);
  }
  50% {
    box-shadow: 0 4px 8px rgba(245, 108, 108, 0.5);
    transform: translateY(-1px);
  }
  100% {
    box-shadow: 0 2px 4px rgba(245, 108, 108, 0.3);
  }
}

.inventory-images h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 500;
}

.upload-area {
  border: 2px dashed #dcdfe6;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  background: #fafafa;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #999;
}

.upload-icon {
  font-size: 32px;
}

.upload-text {
  font-size: 14px;
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.dialog-footer .el-button {
  flex: 1;
  height: 44px;
}

:deep(.el-dialog__body) {
  padding: 20px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}

:deep(.el-select),
:deep(.el-input) {
  width: 100%;
}
</style>
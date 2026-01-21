<template>
    <el-dialog v-model="visible" title="资产详情" width="800px" :before-close="handleClose">
        <div v-loading="loading">
            <el-descriptions :column="2" border>
                <el-descriptions-item label="资产名称">
                    {{ assetDetail.name || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="资产编号">
                    {{ assetDetail.asset_code || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="资产类别">
                    {{ assetDetail.category_name || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="资产型号">
                    {{ assetDetail.model || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="品牌">
                    {{ assetDetail.brand || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="序列号">
                    {{ assetDetail.serial_number || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="规格">
                    {{ assetDetail.specifications || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="财务编码">
                    {{ assetDetail.financial_code || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="存放位置">
                    {{ assetDetail.location_name || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="使用部门">
                    {{ assetDetail.department_name || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="状态">
                    <el-tag effect="dark" :type="getStatusType(assetDetail.status)">
                        {{ getStatusLabel(assetDetail.status) }}
                    </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="使用人">
                    {{ assetDetail.owner || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="购买价格">
                    {{ assetDetail.purchase_price ? `¥${assetDetail.purchase_price}` : '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="创建时间">
                    {{ assetDetail.created_at ? formatDate(assetDetail.created_at) : '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="更新时间">
                    {{ assetDetail.updated_at ? formatDate(assetDetail.updated_at) : '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="备注" :span="2">
                    {{ assetDetail.remarks || '-' }}
                </el-descriptions-item>
            </el-descriptions>

            <!-- 资产图片展示 -->
            <div v-if="assetDetail.image_urls && assetDetail.image_urls.length > 0" style="margin-top: 20px;">
                <h4>资产图片</h4>
                <el-image v-for="(url, index) in assetDetail.image_urls" :key="index" :src="url"
                    :preview-src-list="assetDetail.image_urls" :initial-index="index" fit="cover"
                    style="width: 100px; height: 100px; margin-right: 10px; margin-bottom: 10px;" preview-teleported />
            </div>
        </div>

        <template #footer>
            <span class="dialog-footer">
                <el-button @click="handleClose">关闭</el-button>
            </span>
        </template>
    </el-dialog>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { GetAssetById } from '@/api/assets'
import { ElMessage } from 'element-plus'

defineOptions({
    name: '资产详情'
})

const visible = ref(false)
const loading = ref(false)
const assetDetail = reactive({})

const statusData = [
    { label: '在库', value: '0', type: 'primary' },
    { label: '使用中', value: '1', type: 'success' },
    { label: '维修中', value: '2', type: 'warning' },
    { label: '报废', value: '3', type: 'danger' },
    { label: '其他', value: '4', type: 'info' },
]

// 根据 status 获取标签类型
function getStatusType(status) {
    const statusItem = statusData.find(item => item.value === status)
    return statusItem ? statusItem.type : 'info'
}

// 根据 status 获取标签文本
function getStatusLabel(status) {
    const statusItem = statusData.find(item => item.value === status)
    return statusItem ? statusItem.label : '未知状态'
}

// 格式化日期
function formatDate(dateString) {
    if (!dateString) return '-'
    const date = new Date(dateString)
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    })
}

// 显示资产详情
async function show(assetId) {
    console.log(assetId)
    visible.value = true
    loading.value = true

    try {
        const response = await GetAssetById(assetId)
        Object.assign(assetDetail, response)
    } catch (error) {
        ElMessage.error('获取资产详情失败：' + error.message)
        handleClose()
    } finally {
        loading.value = false
    }
}

// 关闭弹窗
function handleClose() {
    visible.value = false
    // 清空数据
    Object.keys(assetDetail).forEach(key => {
        delete assetDetail[key]
    })
}

// 暴露方法给父组件
defineExpose({
    show
})
</script>

<style scoped>
.dialog-footer {
    text-align: right;
}
</style>
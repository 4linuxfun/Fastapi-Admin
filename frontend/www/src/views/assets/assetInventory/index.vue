<template>
    <div>
        <!-- 查询和新增按钮 -->
        <el-row>
            <el-form :model="search" :inline="true" ref="searchRef">
                <el-form-item label="批次名称" prop="batch_name">
                    <el-input v-model="search.batch_name" clearable placeholder="请输入批次名称" />
                </el-form-item>
                <el-form-item label="状态" prop="status">
                    <el-select v-model="search.status" placeholder="请选择状态" style="width: 150px;" clearable
                        @change="handleSearch" :loading="loading">
                        <el-option v-for="item in statusData" :key="item.value" :label="item.label"
                            :value="item.value" />
                    </el-select>
                </el-form-item>
                <el-form-item label="创建人" prop="created_by_user_id">
                    <el-input v-model="search.created_by_user_id" clearable placeholder="请输入创建人ID" />
                </el-form-item>
                <el-form-item label="开始日期" prop="start_date">
                    <el-date-picker v-model="search.start_date" type="date" placeholder="开始日期" value-format="YYYY-MM-DD" />
                </el-form-item>
                <el-form-item label="结束日期" prop="end_date">
                    <el-date-picker v-model="search.end_date" type="date" placeholder="结束日期" value-format="YYYY-MM-DD" />
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" @click="handleSearch" :icon="Search" :loading="loading">搜索</el-button>
                    <el-button @click="handleReset" :icon="RefreshRight" :loading="loading">重置</el-button>
                </el-form-item>
            </el-form>
        </el-row>
        <el-row>
            <el-col :span="24">
                <el-button type="primary" @click="addBatchRef.open()" :icon="Plus">新增盘点批次</el-button>
            </el-col>
        </el-row>
        <el-row>
            <el-col :span="24">
                <el-table :data="tableData" style="width: 100%" v-loading="loading" border>
                    <el-table-column prop="batch_id" label="批次ID" width="100" />
                    <el-table-column prop="batch_name" label="批次名称" width="200" />
                    <el-table-column prop="status" label="状态" width="120">
                        <template #default="scope">
                            <el-tag :type="getStatusType(scope.row.status)">{{ getStatusLabel(scope.row.status)
                                }}</el-tag>
                        </template>
                    </el-table-column>
                    <el-table-column prop="start_date" label="开始日期" width="120">
                        <template #default="scope">
                            {{ formatDate(scope.row.start_date) }}
                        </template>
                    </el-table-column>
                    <el-table-column prop="end_date" label="结束日期" width="120">
                        <template #default="scope">
                            {{ formatDate(scope.row.end_date) }}
                        </template>
                    </el-table-column>
                    <el-table-column prop="created_by_user_id" label="创建人" width="120" />
                    <el-table-column prop="created_at" label="创建时间" width="180">
                        <template #default="scope">
                            {{ formatDateTime(scope.row.created_at) }}
                        </template>
                    </el-table-column>
                    <el-table-column label="操作" width="280" fixed="right">
                        <template #default="scope">
                            <el-button type="primary" size="small" @click="editBatch(scope.row)">编辑</el-button>
                            <el-button type="success" size="small" @click="viewRecords(scope.row)">查看记录</el-button>
                            <el-button type="danger" size="small" @click="handleDelete(scope.row)">删除</el-button>
                        </template>
                    </el-table-column>
                </el-table>
            </el-col>
        </el-row>
        <el-row>
            <el-col :span="24">
                <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize"
                    :page-sizes="[10, 20, 50, 100]" :small="false" :disabled="false" :background="true"
                    layout="total, sizes, prev, pager, next, jumper" :total="total" @size-change="freshCurrentPage"
                    @current-change="freshCurrentPage" />
            </el-col>
        </el-row>
    </div>

    <!-- 新增/编辑盘点批次对话框 -->
    <add-batch ref="addBatchRef" @refresh="freshCurrentPage" />
    
    <!-- 盘点记录对话框 -->
    <inventory-records v-model:visible="recordsDialogVisible" :batch-data="selectedBatch" />
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Search, RefreshRight, Plus } from '@element-plus/icons-vue'
import usePagination from '@/composables/usePagination'
import AddBatch from './AddBatch.vue'
import InventoryRecords from './InventoryRecords.vue'
import { GetInventoryBatches, DeleteInventoryBatch } from '@/api/assets'
import { ConfirmDel } from '@/utils/request'

defineOptions({
    name: '资产盘点'
})

const searchForm = reactive({
    batch_name: null,
    status: null,
    created_by_user_id: null,
    start_date: null,
    end_date: null
})

const searchRef = ref()
const addBatchRef = ref(null)

// 盘点记录对话框状态
const recordsDialogVisible = ref(false)
const selectedBatch = ref({})

const {
    search,
    tableData,
    currentPage,
    pageSize,
    orderModel,
    total,
    loading,
    freshCurrentPage,
    handleSearch
} = usePagination('/api/assets/inventory/batches/search', searchForm, 'desc')

const statusData = [
    { label: '进行中', value: 'active', type: 'primary' },
    { label: '已完成', value: 'completed', type: 'success' },
    { label: '已关闭', value: 'closed', type: 'warning' }
]

// 根据状态获取标签类型
function getStatusType(status) {
    const statusItem = statusData.find(item => item.value === status)
    return statusItem ? statusItem.type : 'info'
}

// 根据状态获取标签文本
function getStatusLabel(status) {
    const statusItem = statusData.find(item => item.value === status)
    return statusItem ? statusItem.label : status
}

// 格式化日期
function formatDate(dateStr) {
    if (!dateStr) return '-'
    return new Date(dateStr).toLocaleDateString('zh-CN')
}

// 格式化日期时间
function formatDateTime(dateStr) {
    if (!dateStr) return '-'
    return new Date(dateStr).toLocaleString('zh-CN')
}

// 编辑批次
function editBatch(batch) {
    addBatchRef.value.open(batch)
}

// 查看盘点记录
function viewRecords(batch) {
    selectedBatch.value = {
        id: batch.batch_id,
        batch_name: batch.batch_name,
        status: batch.status,
        start_date: batch.start_date,
        end_date: batch.end_date
    }
    recordsDialogVisible.value = true
}

// 删除盘点批次
async function handleDelete(batch) {
    console.log('删除盘点批次：', batch)
    try {
        await ConfirmDel('确定删除盘点批次: ' + batch.batch_name + '?', DeleteInventoryBatch, batch.batch_id)
    } catch (e) {
        console.log('删除盘点批次失败', e)
        return false
    }
    await freshCurrentPage()
}

// 重置搜索表单
function handleReset() {
    searchRef.value.resetFields()
    handleSearch()
}

onMounted(() => {
    handleSearch()
})
</script>

<style scoped>
.el-row {
    margin-bottom: 20px;
}
</style>
<template>
    <div>
        <!-- 查询和新增按钮 -->
        <el-row>
            <el-form :model="search" :inline="true" ref="searchRef">
                <el-form-item label="资产类别" prop="category_code">
                    <el-tree-select v-model="search.category_code" :data="categoryData" :render-after-expand="false"
                        :props="{ label: 'name' }" value-key="code" check-strictly style="width: 200px"
                        @change="handleSearch()" clearable />
                </el-form-item>
                <el-form-item label="资产名称" prop="name">
                    <el-input v-model="search.name" clearable />
                </el-form-item>
                <el-form-item label="资产编号" prop="asset_code">
                    <el-input v-model="search.asset_code" clearable />
                </el-form-item>
                <el-form-item label="资产型号" prop="model">
                    <el-input v-model="search.model" clearable />
                </el-form-item>
                <el-form-item label="品牌" prop="brand">
                    <el-input v-model="search.brand" clearable />
                </el-form-item>
                <el-form-item label="序列号" prop="serial_number">
                    <el-input v-model="search.serial_number" clearable />
                </el-form-item>
                <el-form-item label="财务编码" prop="financial_code">
                    <el-input v-model="search.financial_code" clearable />
                </el-form-item>
                <el-form-item label="使用人" prop="owner">
                    <el-input v-model="search.owner" clearable />
                </el-form-item>
                <el-form-item label="资产状态" prop="status">
                    <el-select v-model="search.status" placeholder="请选择状态" style="width: 150px;" clearable
                        @change="handleSearch">
                        <el-option v-for="item in statusData" :key="item.value" :label="item.label"
                            :value="item.value" />
                    </el-select>
                </el-form-item>
                <el-form-item label="存放位置" prop="location_code">
                    <el-tree-select v-model="search.location_code" :data="locationData" :render-after-expand="false"
                        :props="{ label: 'name' }" value-key="code" check-strictly style="width: 200px"
                        @change="handleSearch()" clearable />
                </el-form-item>
                <el-form-item label="使用部门" prop="department_code">
                    <el-tree-select v-model="search.department_code" :data="departmentData" :render-after-expand="false"
                        :props="{ label: 'name' }" value-key="code" check-strictly style="width: 200px"
                        @change="handleSearch()" clearable />
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" @click="handleSearch" :icon="Search">搜索</el-button>
                    <el-button type="primary" @click="searchRef.resetFields()" :icon="RefreshRight">重置</el-button>
                </el-form-item>
            </el-form>
        </el-row>
        <el-row>
            <el-button v-permission="'assets:add'" type="primary" @click="handleAdd" :icon="Plus">资产录入</el-button>
            <el-button v-permission="'assets:allocation'" type="primary" @click="assetAllocationRef.show()"
                :icon="Upload">资产领用</el-button>
            <el-button v-permission="'assets:return'" type="primary" @click="assetReturnRef.show()"
                :icon="Download">资产退回</el-button>
            <el-button v-permission="'assets:allocation'" type="primary" @click="assetTransferRef.show()"
                :icon="Connection">资产转移</el-button>
            <el-button v-permission="'assets:disposal'" type="danger" @click="assetDisposalRef.show()"
                :icon="Delete">资产报废</el-button>
            <el-button v-permission="'assets:import'" @click="assetImportRef.show()"
                :icon="DocumentAdd">批量导入</el-button>
            <el-button v-permission="'assets:export'" @click="handleExport" :loading="exportLoading">批量导出
                <template #icon>
                    <svg t="1747794634776" class="icon" viewBox="0 0 1024 1024" version="1.1"
                        xmlns="http://www.w3.org/2000/svg" p-id="1588" width="256" height="256">
                        <path
                            d="M445.269333 439.466667H341.461333a13.525333 13.525333 0 0 1-7.808-2.304c-17.792-12.672-17.621333-33.152-6.186666-44.757334l164.821333-213.504a27.605333 27.605333 0 0 1 39.04-0.298666l0.298667 0.298666L696.533333 392.533333a27.648 27.648 0 1 1-19.626666 46.976h-98.176v208.469334a13.824 13.824 0 0 1-13.824 13.824h-105.813334a13.824 13.824 0 0 1-13.824-13.824v-208.469334zM261.546667 640.426667v109.056c0 7.637333 6.186667 13.824 13.824 13.824h472.832a13.824 13.824 0 0 0 13.824-13.824V640.426667c0-8.234667 6.656-14.890667 14.890666-14.890667h61.610667c8.192 0 14.848 6.656 14.848 14.890667v199.04a13.824 13.824 0 0 1-13.824 13.824H184.490667A13.824 13.824 0 0 1 170.666667 839.509333v-199.04c0-8.234667 6.656-14.890667 14.848-14.890666h61.141333c8.192 0 14.848 6.656 14.848 14.890666z"
                            fill="#000000" p-id="1589"></path>
                    </svg>
                </template>
            </el-button>
            <el-button v-permission="'assets:read'" @click="userAssetLogsRef.show()" :icon="User">用户领用记录</el-button>
        </el-row>

        <!-- 资产信息表格 -->
        <el-table v-loading="loading" :data="tableData" style="width: 100%;margin-top: 10px;" border>
            <el-table-column type="index" label="#"></el-table-column>
            <el-table-column prop="name" label="资产名称"></el-table-column>
            <el-table-column prop="asset_code" label="资产编号" width="120"></el-table-column>
            <el-table-column prop="category_name" label="资产类别" width="100"></el-table-column>
            <el-table-column prop="model" label="资产型号"></el-table-column>
            <el-table-column prop="brand" label="品牌"></el-table-column>
            <el-table-column prop="serial_number" label="序列号"></el-table-column>
            <el-table-column prop="specifications" label="规格"></el-table-column>
            <el-table-column prop="financial_code" label="财务编码"></el-table-column>
            <el-table-column prop="location_name" label="存放位置"></el-table-column>
            <el-table-column prop="department_name" label="使用部门" width="120"></el-table-column>
            <el-table-column label="状态">
                <template #default="scope">
                    <el-tag effect="dark" :type="getStatusType(scope.row.status)">{{ getStatusLabel(scope.row.status)
                    }}</el-tag>
                </template>
            </el-table-column>
            <el-table-column prop="remarks" label="备注"></el-table-column>
            <el-table-column prop="owner" label="使用人"></el-table-column>
            <el-table-column fixed="right" label="操作" width="240">
                <template #default="scope">
                    <el-button v-permission="'assets:add'" link v-if="scope.row.status === '0'" type="primary"
                        @click="addAssetRef.edit(scope.row.id)">编辑</el-button>
                    <el-button link type="info" @click="assetDetailRef.show(scope.row.id)">详情</el-button>
                    <el-button link @click="assetLogsRef.show(scope.row.id)">记录</el-button>
                </template>
            </el-table-column>
        </el-table>
        <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total" background
            layout="total,prev,pager,next,sizes,jumper" style="margin-top: 10px;" />
    </div>

    <add-asset ref="addAssetRef" @success="freshCurrentPage" />
    <asset-allocation ref="assetAllocationRef" @success="freshCurrentPage" />
    <asset-return ref="assetReturnRef" @success="freshCurrentPage" />
    <asset-disposal ref="assetDisposalRef" @success="freshCurrentPage" />
    <asset-transfer ref="assetTransferRef" @success="freshCurrentPage" />
    <asset-logs ref="assetLogsRef" />
    <assets-import ref="assetImportRef" />
    <user-asset-logs ref="userAssetLogsRef" />
    <asset-detail ref="assetDetailRef" />
</template>

<script setup>
defineOptions({
    name: '资产维护'
})
import { ref, reactive, onMounted } from 'vue'
import { Search, RefreshRight, Plus, Upload, Download, Delete, DocumentAdd, User, Connection } from '@element-plus/icons-vue'
import usePagination from '@/composables/usePagination'
import AddAsset from './AddAsset.vue'
import AssetAllocation from './assetAllocation/index.vue'
import AssetReturn from './assetReturn/index.vue'
import AssetDisposal from './assetDisposal/index.vue'
import AssetTransfer from './assetTransfer/index.vue'
import AssetLogs from './assetLogs.vue'
import AssetsImport from './assetsImport.vue'
import UserAssetLogs from './userAssetLogs.vue'
import AssetDetail from './AssetDetail.vue'
import { GetAssetCategoryTree, GetAssetLocationTree, GetAssetDepartmentTree, GetAssetExport } from '@/api/assets'

const searchForm = reactive({
    name: null,
    asset_code: null,
    model: null,
    brand: null,
    serial_number: null,
    financial_code: null,
    owner: null,
    status: null,
    department_code: null
})
const searchRef = ref()
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
} = usePagination('/api/assets/search', searchForm, 'desc')

const addAssetRef = ref(null)
const assetAllocationRef = ref(null)
const assetReturnRef = ref(null)
const assetDisposalRef = ref(null)
const assetTransferRef = ref(null)
const assetLogsRef = ref(null)
const assetImportRef = ref(null)
const userAssetLogsRef = ref(null)
const assetDetailRef = ref(null)
const statusData = [
    { label: '在库', value: '0', type: 'primary' },
    { label: '使用中', value: '1', type: 'success' },
    { label: '维修中', value: '2', type: 'warning' },
    { label: '报废', value: '3', type: 'danger' },
    { label: '其他', value: '4', type: 'info' },
]
const categoryData = ref([])
const locationData = ref([])
const departmentData = ref([])
const exportLoading = ref(false)

// 根据 status 获取标签类型
function getStatusType(status) {
    const statusItem = statusData.find(item => item.value === status);
    return statusItem ? statusItem.type : 'info'; // 默认类型为 'info'
}

async function handleExport() {
    try {
        // 添加加载状态
        exportLoading.value = true;

        // 模拟等待时间
        //await new Promise(resolve => setTimeout(resolve, 3000));

        const response = await GetAssetExport(); // 请求接口获取数据

        // 创建 Blob 对象，指定类型为 Excel 文件
        const blob = new Blob([response.data], {
            type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        });

        // 创建一个隐藏的 <a> 标签用于下载
        const downloadUrl = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.setAttribute('download', response.filename); // 设置下载文件名
        document.body.appendChild(link);
        link.click();

        // 清理 URL 对象和 DOM 元素
        window.URL.revokeObjectURL(downloadUrl);
        document.body.removeChild(link);
    } catch (error) {
        ElNotification({
            title: '错误',
            message: '导出失败，请稍后再试: ' + error.message,
            type: 'error'
        });
    } finally {
        // 移除加载状态
        exportLoading.value = false;
    }
}

// 根据 status 获取标签文本
function getStatusLabel(status) {
    const statusItem = statusData.find(item => item.value === status);
    return statusItem ? statusItem.label : '未知状态'; // 默认文本为 '未知状态'
}

function handleAdd() {
    console.log('handleAdd')
    addAssetRef.value.add()
}

onMounted(async () => {
    categoryData.value = await GetAssetCategoryTree()
    locationData.value = await GetAssetLocationTree()
    departmentData.value = await GetAssetDepartmentTree()
    await handleSearch()
})
</script>

<style scoped></style>
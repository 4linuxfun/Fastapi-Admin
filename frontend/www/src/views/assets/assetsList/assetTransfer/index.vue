<!-- 资产转移页面 -->
<template>
    <el-dialog v-model="visible" title="资产转移" width="70%" class="form-inline" destroy-on-close @closed="handleClose">
        <el-row>
            <el-form :model="search" :inline="true" ref="searchRef">
                <el-form-item label="资产类别" prop="category_code">
                    <el-tree-select v-model="search.category_code" :data="categoryData" :render-after-expand="false"
                        :props="{ label: 'name' }" value-key="code" check-strictly style="width: 200px"
                        @change="handleSearch()" clearable />
                </el-form-item>
                <el-form-item label="资产编号" prop="asset_code">
                    <el-input v-model="search.asset_code" placeholder="请输入资产编号" clearable />
                </el-form-item>
                <el-form-item label="资产名称" prop="name">
                    <el-input v-model="search.name" placeholder="请输入资产名称" clearable />
                </el-form-item>
                <el-form-item label="资产型号" prop="model">
                    <el-input v-model="search.model" placeholder="请输入资产型号" clearable />
                </el-form-item>
                <el-form-item label="品牌" prop="brand">
                    <el-input v-model="search.brand" placeholder="请输入品牌" clearable />
                </el-form-item>
                <el-form-item label="序列号" prop="serial_number">
                    <el-input v-model="search.serial_number" placeholder="请输入序列号" clearable />
                </el-form-item>
                <el-form-item label="使用人" prop="owner">
                    <el-input v-model="search.owner" placeholder="请输入使用人" clearable />
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" @click="handleSearch" :icon="Search">搜索</el-button>
                    <el-button type="primary" @click="searchRef.resetFields()" :icon="RefreshRight">重置</el-button>
                </el-form-item>
            </el-form>
        </el-row>

        <!-- 资产信息表格 -->
        <el-table v-loading="loading" :data="tableData" style="width: 100%;margin-top: 10px;" border>
            <el-table-column type="index" />
            <el-table-column label="操作" align="center">
                <template #default="scope">
                    <el-button link type="primary" @click="handleTransfer(scope.row)">转移</el-button>
                </template>
            </el-table-column>
            <el-table-column prop="name" label="资产名称"></el-table-column>
            <el-table-column prop="asset_code" label="资产编号"></el-table-column>
            <el-table-column prop="category_name" label="资产类别"></el-table-column>
            <el-table-column prop="model" label="资产型号"></el-table-column>
            <el-table-column prop="brand" label="品牌"></el-table-column>
            <el-table-column prop="serial_number" label="序列号"></el-table-column>
            <el-table-column prop="financial_code" label="财务编码"></el-table-column>
            <el-table-column prop="location_name" label="存放位置"></el-table-column>
            <el-table-column prop="department_name" label="使用部门"></el-table-column>
            <el-table-column prop="owner" label="使用人"></el-table-column>
            <el-table-column fixed="right" label="查看记录" width="120">
                <template #default="scope">
                    <el-button link @click="assetLogsRef.show(scope.row.id)">记录</el-button>
                </template>
            </el-table-column>
        </el-table>
        <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total" background
            layout="total,prev,pager,next,sizes,jumper" style="margin-top: 10px;" />

        <transfer-dialog ref="transferDialogRef" @success="freshCurrentPage" />
        <assetLogs ref="assetLogsRef" />
    </el-dialog>
</template>

<script setup>
import { ref, reactive } from "vue"
import { Search, RefreshRight } from '@element-plus/icons-vue'
import usePagination from '@/composables/usePagination'
import { GetAssetCategoryTree } from '@/api/assets'
import TransferDialog from "./TransferDialog.vue"
import assetLogs from "../assetLogs.vue"

const emits = defineEmits(["success"])
const visible = ref(false)
const transferDialogRef = ref(null)
const assetLogsRef = ref(null)

// 监听对话框关闭事件
function handleClose() {
    // 通知父组件刷新数据
    emits("success")
}
const searchForm = reactive({
    name: null,
    asset_code: null,
    category_code: null,
    model: null,
    brand: null,
    serial_number: null,
    owner: null,
    status: 1, // 只查询已领用的资产
})
const {
    search,
    tableData,
    currentPage,
    pageSize,
    orderModel,
    total,
    loading,
    freshCurrentPage,
    handleSearch,
    searchRef
} = usePagination('/api/assets/search', searchForm)

const categoryData = ref([])

// 初始化资产类别树
async function initCategoryTree() {
    categoryData.value = await GetAssetCategoryTree()
}

// 处理资产转移
function handleTransfer(row) {
    transferDialogRef.value.show(row)
}

// 显示资产转移对话框
async function show(assetId) {
    visible.value = true
    tableData.value = []
    // 重置搜索表单
    Object.keys(searchForm).forEach(key => {
        if (key === 'status') {
            searchForm[key] = 1 // 只查询已领用的资产
        } else {
            searchForm[key] = null
        }
    })
    // 如果传入了资产ID，则设置资产编号搜索条件
    if (assetId) {
        search.asset_code = assetId
    }
    try {
        // 先执行查询，确保弹出后加载数据
        await handleSearch()
        // 再加载类别树
        await initCategoryTree()
    } catch (err) {
        console.log("获取数据失败", err)
    }
}

// 暴露方法给父组件
defineExpose({
    show
})
</script>

<style scoped>
.form-inline .el-form-item {
    margin-right: 10px;
}
</style>
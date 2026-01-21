<!-- 资产领用页面 -->
<template>
    <el-dialog v-model="visible" title="资产报废" width="70%" class="form-inline" destroy-on-close>
        <el-row>
            <el-form :model="search" :inline="true" ref="searchRef">
                <el-form-item label="资产类别" prop="category_code">
                    <el-tree-select v-model="search.category_code" :data="categoryData" :render-after-expand="false"
                        :props="{ label: 'name' }" value-key="code" check-strictly style="width: 200px"
                        @change="handleSearch()" />
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
                <el-form-item label="财务编码" prop="financial_code">
                    <el-input v-model="search.financial_code" placeholder="请输入财务编码" clearable />
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
                    <el-button link type="primary" @click="handleDisposal(scope.row)">报废</el-button>
                </template>
            </el-table-column>
            <el-table-column prop="name" label="资产名称" width="100"></el-table-column>
            <el-table-column prop="asset_code" label="资产编号" width="120"></el-table-column>
            <el-table-column prop="category_name" label="资产类别"></el-table-column>
            <el-table-column prop="model" label="资产型号"></el-table-column>
            <el-table-column prop="brand" label="品牌"></el-table-column>
            <el-table-column prop="serial_number" label="序列号"></el-table-column>
            <el-table-column prop="financial_code" label="财务编码"></el-table-column>
            <el-table-column prop="location_name" label="存放位置"></el-table-column>
            <el-table-column prop="remarks" label="备注"></el-table-column>
            <el-table-column fixed="right" label="操作记录">
                <template #default="scope">
                    <el-button link @click="assetLogsRef.show(scope.row.id)">记录</el-button>
                </template>
            </el-table-column>
        </el-table>
        <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total" background
            layout="total,prev,pager,next,sizes,jumper" style="margin-top: 10px;" />

        <Disposal ref="disposalRef" @success="freshCurrentPage" />
        <assetLogs ref="assetLogsRef" />
    </el-dialog>
</template>

<script setup>
import { ref, reactive } from "vue"
import { Search, RefreshRight } from '@element-plus/icons-vue'
import usePagination from '@/composables/usePagination'
import { GetAssetCategoryTree } from '@/api/assets'
import Disposal from "./Disposal.vue"
import assetLogs from "../assetLogs.vue"

const emits = defineEmits(["success"])
const visible = ref(false)
const disposalRef = ref(null)
const assetLogsRef = ref(null)
// 只有状态为0（在库）状态的才能报废
const searchForm = reactive({
    name: null,
    asset_code: null,
    serial_number: null,
    financial_code: null,
    category_code: null,
    model: null,
    brand: null,
    status: 0,
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
    handleSearch
} = usePagination('/api/assets/search', searchForm, 'desc')
const categoryData = ref([])
const searchRef = ref(null)

function handleDisposal(row) {
    disposalRef.value.show(row)
}

async function show() {
    visible.value = true
    tableData.value = []
    try {
        await handleSearch()
        categoryData.value = await GetAssetCategoryTree()
    } catch (err) {
        console.log("获取分类树失败")
        return false
    }

}



defineExpose({
    show
})

</script>

<style scoped>
.form-inline .el-form-item {
    margin-right: 10px;
}
</style>

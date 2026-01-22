<template>
    <!-- <el-form ref="searchRef" :model="search" :inline="true">
        <el-form-item label="分类名称" prop="name">
            <el-input v-model="search.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="分类编码" prop="code">
            <el-input v-model="search.code" placeholder="请输入分类编码" />
        </el-form-item>
        <el-form-item>
            <el-button type="primary" icon="Search" @click="handleSearch">查询</el-button>
            <el-button type="primary" icon="RefreshRight" @click="searchRef.resetFields()">重置</el-button>
        </el-form-item>
    </el-form> -->

    <el-row>
        <el-button v-permission="'assetsLocation:add'" icon="Plus" type="primary" @click="handleAdd">新增</el-button>
        <el-button type="primary">导出</el-button>
        <el-button type="primary">导入</el-button>
    </el-row>
    <!-- 资产信息表格 -->
    <el-table :data="categoryData" style="width: 100%;margin-top: 10px;" border row-key="id">
        <el-table-column prop="name" label="位置名称"></el-table-column>
        <el-table-column fixed="right" label="操作">
            <template #default="scope">
                <el-button v-permission="'assetsLocation:update'" link type="primary"
                    @click="handleEdit(scope.row)">编辑</el-button>
                <el-button v-permission="'assetsLocation:delete'" link type="primary"
                    @click="handleDelete(scope.row)">删除</el-button>
                <el-button v-permission="'assetsLocation:add'" link type="primary"
                    @click="handleAddChild(scope.row)">添加下一级</el-button>
            </template>
        </el-table-column>
    </el-table>

    <add-location ref="addLocationRef" @close="refresh()" />

</template>

<script setup>
defineOptions({
    name: '资产位置'
})
import { ref, reactive, onMounted } from 'vue'
import { GetAssetLocationTree } from '@/api/assets'
import { ConfirmDel } from '@/utils/request'
import AddLocation from './AddLocation.vue'
import { DeleteAssetLocation } from '@/api/assets'


const addLocationRef = ref()
const categoryData = ref([])


function handleAdd() {
    console.log('新增')
    addLocationRef.value.add()
}

function handleAddChild(row) {
    console.log('添加下一级', row)
    addLocationRef.value.addChild(row)
}

// 逻辑删除，子类也会同步标记为删除
async function handleDelete(category) {
    console.log('删除位置：', category)
    try {
        await ConfirmDel('确定删除位置:' + category.name + '?', DeleteAssetLocation, category.id)
    } catch (e) {
        console.log('删除位置失败', e)
        return false
    }
    await refresh()
}

function handleEdit(row) {
    addLocationRef.value.edit(row)
}

async function refresh() {
    try {
        const res = await GetAssetLocationTree()
        categoryData.value = res
    } catch (err) {
        console.log("获取分类树失败")
        return false
    }
}

onMounted(async () => {
    await refresh()
})
</script>

<style scoped></style>

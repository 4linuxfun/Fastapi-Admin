<template>
    <el-row>
        <el-button v-permission="'assetsDepartment:add'" icon="Plus" type="primary" @click="handleAdd">新增</el-button>
        <el-button type="primary">导出</el-button>
        <el-button type="primary">导入</el-button>
    </el-row>
    <!-- 部门信息表格 -->
    <el-table :data="departmentData" style="width: 100%;margin-top: 10px;" border row-key="id">
        <el-table-column prop="name" label="部门名称"></el-table-column>
        <el-table-column fixed="right" label="操作">
            <template #default="scope">
                <el-button v-permission="'assetsDepartment:update'" link type="primary"
                    @click="handleEdit(scope.row)">编辑</el-button>
                <el-button v-permission="'assetsDepartment:delete'" link type="primary"
                    @click="handleDelete(scope.row)">删除</el-button>
                <el-button v-permission="'assetsDepartment:add'" link type="primary"
                    @click="handleAddChild(scope.row)">添加下一级</el-button>
            </template>
        </el-table-column>
    </el-table>

    <add-department ref="addDepartmentRef" @close="refresh()" />

</template>

<script setup>
defineOptions({
    name: '资产部门'
})
import { ref, reactive, onMounted } from 'vue'
import { GetAssetDepartmentTree } from '@/api/assets'
import { ConfirmDel } from '@/utils/request'
import AddDepartment from './AddDepartment.vue'
import { DeleteAssetDepartment } from '@/api/assets'


const addDepartmentRef = ref()
const departmentData = ref([])


function handleAdd() {
    console.log('新增')
    addDepartmentRef.value.add()
}

function handleAddChild(row) {
    console.log('添加下一级', row)
    addDepartmentRef.value.addChild(row)
}

// 逻辑删除，子类也会同步标记为删除
async function handleDelete(department) {
    console.log('删除部门：', department)
    try {
        await ConfirmDel('确定删除部门:' + department.name + '?', DeleteAssetDepartment, department.id)
    } catch (e) {
        console.log('删除部门失败', e)
        return false
    }
    await refresh()
}

function handleEdit(row) {
    addDepartmentRef.value.edit(row)
}

async function refresh() {
    try {
        const res = await GetAssetDepartmentTree()
        departmentData.value = res
    } catch (err) {
        console.log("获取部门树失败")
        return false
    }
}

onMounted(async () => {
    await refresh()
})
</script>

<style scoped></style>
<template>
    <el-dialog v-model="visible" :title="title" width="500" destroy-on-close>
        <el-form :model="department">
            <el-form-item label="父级节点" prop="parent_id">
                <el-tree-select :disabled="isEdit" v-model="department.parent_id" :data="assetsDepartmentTree"
                    :check-strictly="true" :props="{ value: 'id', label: 'name' }" />
            </el-form-item>
            <el-form-item label="部门名称" prop="name">
                <el-input v-model="department.name" placeholder="请输入" />
            </el-form-item>
        </el-form>
        <el-row justify="center">
            <el-button type="danger" @click="visible = false">取消</el-button>
            <el-button type="primary" @click="handleUpdate">确定</el-button>
        </el-row>
    </el-dialog>
</template>

<script setup>
import { ref, reactive } from "vue"
import { GetAssetDepartmentTree, AddNewAssetDepartment, UpdateAssetDepartment } from "@/api/assets"

const emits = defineEmits(["close"])
const visible = ref(false)
const title = ref("")
const isEdit = ref(false)
const assetsDepartmentTree = ref([])
const initDepartment = {
    parent_id: null,
    name: ""
}
const department = reactive(JSON.parse(JSON.stringify(initDepartment)))

async function handleUpdate() {
    visible.value = false
    if (isEdit.value) {
        // 编辑
        try {
            await UpdateAssetDepartment(department)
        } catch (err) {
            console.log("更新部门失败")
            return false
        }
    } else {
        // 新增
        try {
            await AddNewAssetDepartment(department)
        } catch (err) {
            console.log("新增部门失败")
            return false
        }
    }
    emits("close")
}

/**
 * 新增部门
 */
async function add() {
    visible.value = true
    title.value = "新增部门"
    isEdit.value = false
    Object.assign(department, JSON.parse(JSON.stringify(initDepartment)))
    console.log(department)
    try {
        assetsDepartmentTree.value = await GetAssetDepartmentTree()
    } catch (err) {
        console.log("获取部门树失败")
        return false
    }
}

/**
 * 新增下级部门
 */
async function addChild(parentRow) {
    visible.value = true
    title.value = "新增下级部门"
    isEdit.value = false
    Object.assign(department, JSON.parse(JSON.stringify(initDepartment)))
    department.parent_id = parentRow.id
    console.log(department)
    try {
        assetsDepartmentTree.value = await GetAssetDepartmentTree()
    } catch (err) {
        console.log("获取部门树失败")
        return false
    }
}

function edit(data) {
    visible.value = true
    title.value = "编辑部门"
    console.log(data)
    Object.assign(department, JSON.parse(JSON.stringify(data)))
    isEdit.value = true
}

defineExpose({
    add,
    addChild,
    edit
})
</script>

<style scoped></style>
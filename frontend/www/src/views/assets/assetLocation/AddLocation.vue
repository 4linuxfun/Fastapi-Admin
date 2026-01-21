<template>
    <el-dialog v-model="visible" :title="title" width="500" destroy-on-close>
        <el-form :model="location">
            <el-form-item label="父级节点" prop="parent_id">
                <el-tree-select :disabled="isEdit" v-model="location.parent_id" :data="assetsLocationTree"
                    :check-strictly="true" :props="{ value: 'id', label: 'name' }" />
            </el-form-item>
            <el-form-item label="位置名称" prop="name">
                <el-input v-model="location.name" placeholder="请输入" />
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
import { GetAssetLocationTree, AddNewAssetLocation, UpdateAssetLocation } from "@/api/assets"

const emits = defineEmits(["close"])
const visible = ref(false)
const title = ref("")
const isEdit = ref(false)
const assetsLocationTree = ref([])
const initLocation = {
    parent_id: null,
    name: ""
}
const location = reactive(JSON.parse(JSON.stringify(initLocation)))

async function handleUpdate() {
    visible.value = false
    if (isEdit.value) {
        // 编辑
        try {
            await UpdateAssetLocation(location)
        } catch (err) {
            console.log("更新分类失败")
            return false
        }
    } else {
        // 新增
        try {
            await AddNewAssetLocation(location)
        } catch (err) {
            console.log("新增分类失败")
            return false
        }
    }
    emits("close")
}

/**
 * 
 */
async function add() {
    visible.value = true
    title.value = "新增位置"
    isEdit.value = false
    Object.assign(location, JSON.parse(JSON.stringify(initLocation)))
    console.log(location)
    try {
        assetsLocationTree.value = await GetAssetLocationTree()
    } catch (err) {
        console.log("获取位置失败")
        return false
    }

}

/**
 * 新增下级分类
 */
async function addChild(data) {
    visible.value = true
    title.value = "新增下级位置"
    isEdit.value = false
    Object.assign(location, JSON.parse(JSON.stringify(initLocation)))
    location.parent_id = data.id
    console.log(location)
    try {
        assetsLocationTree.value = await GetAssetLocationTree()
    } catch (err) {
        console.log("获取位置失败")
        return false
    }
}

function edit(data) {
    visible.value = true
    title.value = "编辑位置"
    console.log(data)
    Object.assign(location, JSON.parse(JSON.stringify(data)))
    isEdit.value = true
}


defineExpose({
    add,
    addChild,
    edit
})
</script>

<style scoped></style>

<template>
    <el-dialog v-model="visible" :title="title" width="500" destroy-on-close>
        <el-form :model="category">
            <el-form-item label="父级节点" prop="parent_id">
                <el-tree-select :disabled="isEdit" v-model="category.parent_id" :data="categoryTree"
                    :check-strictly="true" :props="{ value: 'id', label: 'name' }" />
            </el-form-item>
            <el-form-item label="分类名称" prop="name">
                <el-input v-model="category.name" placeholder="请输入" />
            </el-form-item>
        </el-form>
        <el-row justify="center">
            <el-button type="danger" @click="visible = false">取消</el-button>
            <el-button type="primary" @click="handleUpdate">确定</el-button>
        </el-row>
    </el-dialog>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue"
import { GetCategoryTree, AddNewCategory, UpdateCategory } from "@/api/category"

const emits = defineEmits(["close"])
const visible = ref(false)
const title = ref("")
const isEdit = ref(false)
const categoryTree = ref([])
const initCategory = {
    parent_id: null,
    name: ""
}
const category = reactive(JSON.parse(JSON.stringify(initCategory)))

async function handleUpdate() {
    visible.value = false
    if (isEdit.value) {
        // 编辑
        try {
            await UpdateCategory(category)
        } catch (err) {
            console.log("更新分类失败")
            return false
        }
    } else {
        // 新增
        try {
            await AddNewCategory(category)
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
    title.value = "新增分类"
    isEdit.value = false
    Object.assign(category, JSON.parse(JSON.stringify(initCategory)))
    console.log(category)
    try {
        categoryTree.value = await GetCategoryTree()
    } catch (err) {
        console.log("获取分类树失败")
        return false
    }

}

/**
 * 新增下级分类
 */
async function addChild(data) {
    visible.value = true
    title.value = "新增下级分类"
    isEdit.value = false
    Object.assign(category, JSON.parse(JSON.stringify(initCategory)))
    category.parent_id = data.id
    console.log(category)
    try {
        categoryTree.value = await GetCategoryTree()
    } catch (err) {
        console.log("获取分类树失败")
        return false
    }
}

function edit(data) {
    visible.value = true
    title.value = "编辑分类"
    console.log(data)
    Object.assign(category, JSON.parse(JSON.stringify(data)))
    isEdit.value = true
}


defineExpose({
    add,
    addChild,
    edit
})
</script>

<style scoped></style>

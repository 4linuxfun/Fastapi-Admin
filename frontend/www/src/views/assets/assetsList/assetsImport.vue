<template>
    <el-dialog v-model="dialogVisible" title="资产批量导入" width="500" destroy-on-close>
        <el-alert title="批量导入提示" type="warning">
            <div class="alert-content">
                <p>用于系统的批量导出和批量导入，请按照模板填写数据，并上传文件！</p>
                <p>资产类别：系统中需要存在此类别，否则无法导入！</p>
                <p>资产编号：必须携带！</p>
                <p>资产状态：在库,使用中,维修中,报废,其他！</p>
                <p>存放位置：系统中需要存在位置，否则无法导入！</p>
            </div>
        </el-alert>
        <a href="/template/资产导入模板.xlsx" download>
            <el-button icon="Document">下载模板</el-button>
        </a>
        <el-upload ref="uploadRef" v-model:file-list="files" action="#" :auto-upload="false" :show-file-list="true"
            accept=".xls,.xlsx" :limit="1" style="margin-top: 5px;">
            <el-button type="primary" icon="Upload">点击上传</el-button>
        </el-upload>

        <template #footer>
            <div class="dialog-footer">
                <el-button type="danger" @click="dialogVisible = false" :disabled="loading">取消</el-button>
                <el-button type="primary" @click="handleSubmit" :loading="loading" :disabled="loading"> 确认 </el-button>
            </div>
        </template>
    </el-dialog>

</template>

<script setup>
import { Upload, Document } from "@element-plus/icons-vue";
import { ref, reactive } from "vue"
import { BulkAssetImport } from "@/api/assets";


const dialogVisible = ref(false)
const uploadRef = ref(null)
const files = ref([])
const loading = ref(false) // 添加loading状态变量

async function handleSubmit() {
    if (files.value.length === 0) {
        ElNotification({
            title: 'error',
            message: '请上传文件',
            type: 'error'
        })
        return
    }
    
    loading.value = true // 设置loading状态为true，禁用按钮并显示加载效果
    
    const formData = new FormData()
    files.value.forEach((file) => {
        formData.append("file", file.raw)
    })
    try {
        await BulkAssetImport(formData)
        ElNotification({
            title: 'success',
            message: '批量导入成功',
            type: 'success'
        })
        dialogVisible.value = false
    } catch (error) {
        console.log(error)
        ElNotification({
            title: 'error',
            message: error.message || '批量导入失败',
            type: 'error'
        })
    } finally {
        loading.value = false // 无论成功或失败，都重置loading状态
    }
}

function show() {
    dialogVisible.value = true
    files.value = []
    loading.value = false // 重置loading状态
}

defineExpose({
    show
})

</script>

<style scoped>
.alert-content {
    white-space: pre-line;
    /* 支持自动换行 */
}

.alert-content p {
    margin: 0;
    line-height: 1.5;
}
</style>

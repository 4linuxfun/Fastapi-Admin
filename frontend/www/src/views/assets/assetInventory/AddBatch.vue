<template>
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑盘点批次' : '新增盘点批次'" width="600px" @close="handleClose">
        <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
            <el-form-item label="批次名称" prop="batch_name">
                <el-input v-model="form.batch_name" placeholder="请输入批次名称" />
            </el-form-item>

            <el-form-item label="开始日期" prop="start_date">
                <el-date-picker v-model="form.start_date" type="date" placeholder="请选择开始日期" style="width: 100%" value-format="YYYY-MM-DD" />
            </el-form-item>
            <el-form-item label="结束日期" prop="end_date">
                <el-date-picker v-model="form.end_date" type="date" placeholder="请选择结束日期" style="width: 100%" value-format="YYYY-MM-DD" />
            </el-form-item>
            <el-form-item label="状态" prop="status" v-if="isEdit">
                <el-select v-model="form.status" placeholder="请选择状态" style="width: 100%">
                    <el-option v-for="item in statusData" :key="item.value" :label="item.label" :value="item.value" />
                </el-select>
            </el-form-item>
        </el-form>
        <template #footer>
            <span class="dialog-footer">
                <el-button @click="handleClose">取消</el-button>
                <el-button type="primary" @click="handleSubmit" :loading="submitLoading">确定</el-button>
            </span>
        </template>
    </el-dialog>
</template>

<script setup>
import { ref, reactive, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { CreateInventoryBatch, UpdateInventoryBatch } from '@/api/assets'

const emit = defineEmits(['refresh'])

const dialogVisible = ref(false)
const isEdit = ref(false)
const submitLoading = ref(false)
const formRef = ref()

const form = reactive({
    batch_id: null,
    batch_name: '',
    start_date: null,
    end_date: null,
    status: 'active'
})

const rules = {
    batch_name: [
        { required: true, message: '请输入批次名称', trigger: 'blur' },
        { min: 2, max: 100, message: '批次名称长度在 2 到 100 个字符', trigger: 'blur' }
    ],
    start_date: [
        { required: true, message: '请选择开始日期', trigger: 'change' }
    ],
    end_date: [
        { required: true, message: '请选择结束日期', trigger: 'change' }
    ]
}

const statusData = [
    { label: '进行中', value: 'active' },
    { label: '已完成', value: 'completed' },
    { label: '已关闭', value: 'closed' }
]

// 打开对话框
function open(batch = null) {
    dialogVisible.value = true
    isEdit.value = !!batch
    
    if (batch) {
        // 编辑模式
        Object.assign(form, {
            batch_id: batch.batch_id,
            batch_name: batch.batch_name,
            start_date: batch.start_date,
            end_date: batch.end_date,
            status: batch.status
        })
    } else {
        // 新增模式
        resetForm()
    }
    
    nextTick(() => {
        formRef.value?.clearValidate()
    })
}

// 重置表单
function resetForm() {
    Object.assign(form, {
        batch_id: null,
        batch_name: '',
        start_date: null,
        end_date: null,
        status: 'active'
    })
}

// 关闭对话框
function handleClose() {
    dialogVisible.value = false
    resetForm()
}

// 提交表单
function handleSubmit() {
    formRef.value.validate(async (valid) => {
        if (!valid) return
        
        // 验证日期
        if (form.end_date && form.start_date && new Date(form.end_date) < new Date(form.start_date)) {
            ElMessage.error('结束日期不能早于开始日期')
            return
        }
        
        submitLoading.value = true
        
        try {
            const submitData = {
                batch_name: form.batch_name,
                start_date: form.start_date,
                end_date: form.end_date
            }
            
            if (isEdit.value) {
                submitData.status = form.status
                await UpdateInventoryBatch(form.batch_id, submitData)
                ElMessage.success('更新盘点批次成功')
            } else {
                await CreateInventoryBatch(submitData)
                ElMessage.success('创建盘点批次成功')
            }
            
            handleClose()
            emit('refresh')
        } catch (error) {
            console.error('提交失败:', error)
            ElMessage.error(isEdit.value ? '更新盘点批次失败' : '创建盘点批次失败')
        } finally {
            submitLoading.value = false
        }
    })
}

// 暴露方法
defineExpose({
    open
})
</script>

<style scoped>
.dialog-footer {
    text-align: right;
}
</style>
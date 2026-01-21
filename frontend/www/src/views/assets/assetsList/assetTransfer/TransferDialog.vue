<template>
    <el-dialog v-model="dialogVisible" title="资产转移" width="50%">
        <el-descriptions border :column="2">
            <el-descriptions-item label="资产编号">{{ assetInfo.asset_code }}</el-descriptions-item>
            <el-descriptions-item label="资产名称">{{ assetInfo.name }}</el-descriptions-item>
            <el-descriptions-item label="资产类别">{{ assetInfo.category_name }}</el-descriptions-item>
            <el-descriptions-item label="当前位置">{{ assetInfo.location_name }}</el-descriptions-item>
            <el-descriptions-item label="当前部门">{{ assetInfo.department_name || '无' }}</el-descriptions-item>
            <el-descriptions-item label="当前使用人">{{ assetInfo.owner || '无' }}</el-descriptions-item>
            <el-descriptions-item label="型号">{{ assetInfo.model }}</el-descriptions-item>
            <el-descriptions-item label="品牌">{{ assetInfo.brand }}</el-descriptions-item>
            <el-descriptions-item label="序列号">{{ assetInfo.serial_number }}</el-descriptions-item>
            <el-descriptions-item label="财务编码">{{ assetInfo.financial_code }}</el-descriptions-item>
            <el-descriptions-item label="规格参数">{{ assetInfo.specifications || '无' }}</el-descriptions-item>
            <el-descriptions-item label="购买日期">{{ assetInfo.purchase_date || '无' }}</el-descriptions-item>
            <el-descriptions-item label="当前状态" :span="2">
                <el-tag :type="assetInfo.status === '1' ? 'success' : 'warning'">
                    {{ assetInfo.status === '1' ? '已领用' : '其他状态' }}
                </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="备注信息" :span="2">{{ assetInfo.remarks || '无' }}</el-descriptions-item>
            <el-descriptions-item label="资产图片" :span="2">
                <div v-if="assetInfo.image_urls && assetInfo.image_urls.length > 0" class="image-gallery">
                    <el-image v-for="(image, index) in assetInfo.image_urls" :key="index" :src="image"
                        :preview-src-list="assetInfo.image_urls" :initial-index="index" fit="cover"
                        class="asset-image" />
                </div>
                <span v-else>无</span>
            </el-descriptions-item>
        </el-descriptions>
        <el-form :model="formData" inline style="margin-top: 20px;" :rules="formRules" ref="formRef" label-width="80px">
            <el-row>
                <el-col :span="12">
                    <el-form-item label="使用位置" prop="location_id">
                        <el-tree-select v-model="formData.location_id" :data="locationData" :render-after-expand="false"
                            :props="{ label: 'name' }" value-key="id" check-strictly style="width: 200px;" />
                    </el-form-item>
                </el-col>
                <el-col :span="12">
                    <el-form-item label="使用部门" prop="department_id">
                        <el-tree-select v-model="formData.department_id" :data="departmentData"
                            :render-after-expand="false" :props="{ label: 'name' }" value-key="id" check-strictly
                            style="width: 200px;" />
                    </el-form-item>
                </el-col>
            </el-row>
            <el-row>
                <el-col :span="12">
                    <el-form-item label="新使用人" prop="owner">
                        <el-input v-model="formData.owner" placeholder="请输入新使用人：工号-姓名" style="width: 200px;" />
                    </el-form-item>
                </el-col>
                <el-col :span="12">
                    <el-form-item label="转移时间" prop="updated_at">
                        <el-date-picker v-model="formData.updated_at" type="datetime" placeholder="请选择日期"
                            style="width: 200px;" />
                    </el-form-item>
                </el-col>
                <el-col :span="12">
                    <el-form-item label="备注信息" prop="remarks">
                        <el-input v-model="formData.remarks" placeholder="请输入转移原因" style="width: 200px;" />
                    </el-form-item>
                </el-col>
            </el-row>
            <el-row>
                <el-col :span="24">
                    <el-form-item label="图片上传" prop="image">
                        <el-upload ref="upload" :file-list="files" action="#" :auto-upload="false"
                            :on-change="handleChange" :on-preview="handlePreview" :on-remove="handleRemove"
                            list-type="picture-card" multiple accept="image/*">
                            <el-icon>
                                <Plus />
                            </el-icon>
                        </el-upload>
                    </el-form-item>
                </el-col>
            </el-row>
        </el-form>
        <template #footer>
            <el-row justify="center">
                <el-button type="danger" @click="dialogVisible = false">取消</el-button>
                <el-button type="primary" @click="handleSubmit">确定</el-button>
            </el-row>
        </template>
    </el-dialog>
</template>

<script setup>
import { ref, reactive } from "vue"
import { Plus } from '@element-plus/icons-vue'
import { GetAssetLocationTree, GetAssetDepartmentTree, AssetTransfer, GetAssetById } from "@/api/assets"
import { ElMessage } from 'element-plus'

const emits = defineEmits(["success"])
const dialogVisible = ref(false)
const assetInfo = reactive({})
const formRef = ref(null)
const initForm = {
    id: null,
    location_id: null,
    department_id: null,
    owner: null,
    updated_at: new Date(),
    remarks: null
}
const formData = reactive({ ...initForm })
const formRules = {
    location_id: [{ required: true, message: '请选择使用位置', trigger: 'change' }],
    department_id: [{ required: true, message: '请选择使用部门', trigger: 'change' }],
    owner: [{ required: true, message: '请输入新使用人', trigger: 'blur' }]
}

const locationData = ref([])
const departmentData = ref([])
const files = ref([])
const upload = ref(null)

// 初始化数据
async function initData() {
    try {
        locationData.value = await GetAssetLocationTree()
        departmentData.value = await GetAssetDepartmentTree()
    } catch (error) {
        console.error('初始化数据失败:', error)
        ElMessage.error('获取位置或部门数据失败')
    }
}

// 显示资产转移对话框
async function show(asset) {
    dialogVisible.value = true
    resetForm()
    
    try {
        // 先初始化数据
        await initData()
        
        // 获取完整的资产信息
        const assetDetail = await GetAssetById(asset.id)
        Object.assign(assetInfo, assetDetail)
        
        // 设置表单初始值
        formData.id = asset.id
        formData.location_id = asset.location_id
        formData.department_id = asset.department_id
        formData.owner = asset.owner
        formData.updated_at = new Date()
        
        console.log('资产转移对话框初始化完成:', { assetInfo, formData })
    } catch (error) {
        console.error('获取资产详情失败:', error)
        ElMessage.error('获取资产详情失败')
        dialogVisible.value = false
    }
}

// 重置表单
function resetForm() {
    Object.assign(formData, initForm)
    files.value = []
    if (formRef.value) {
        formRef.value.resetFields()
    }
    Object.keys(assetInfo).forEach(key => {
        delete assetInfo[key]
    })
}

// 处理文件变更
function handleChange(file, fileList) {
    files.value = fileList
}

// 处理文件预览
function handlePreview(file) {
    const url = file.url || URL.createObjectURL(file.raw)
    window.open(url)
}

// 处理文件移除
function handleRemove(file, fileList) {
    files.value = fileList
}

// 提交表单
async function handleSubmit() {
    if (!formRef.value) return
    
    await formRef.value.validate(async (valid) => {
        if (valid) {
            try {
                const formDataObj = new FormData()
                formDataObj.append('id', formData.id)
                formDataObj.append('location_id', formData.location_id)
                formDataObj.append('department_id', formData.department_id)
                formDataObj.append('owner', formData.owner)
                if (formData.remarks) {
                    formDataObj.append('remarks', formData.remarks)
                }
                
                // 添加文件
                files.value.forEach(file => {
                    if (file.raw) {
                        formDataObj.append(file.name, file.raw)
                    }
                })
                
                await AssetTransfer(formDataObj)
                ElMessage.success('资产转移成功')
                dialogVisible.value = false
                emits('success')
            } catch (error) {
                console.error('资产转移失败:', error)
                ElMessage.error('资产转移失败: ' + (error.message || '未知错误'))
            }
        } else {
            ElMessage.warning('请完善表单信息')
            return false
        }
    })
}

// 暴露方法给父组件
defineExpose({
    show
})
</script>

<style scoped>
.image-gallery {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.asset-image {
    width: 100px;
    height: 100px;
    object-fit: cover;
    border-radius: 4px;
    cursor: pointer;
}

.el-form-item {
    margin-bottom: 15px;
}
</style>
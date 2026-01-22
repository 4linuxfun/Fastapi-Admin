<template>
    <el-dialog v-model="dialogVisible" title="领用" width="50%">
        <el-descriptions border :column="2">
            <el-descriptions-item label="资产编号">{{ assetInfo.asset_code }}</el-descriptions-item>
            <el-descriptions-item label="资产名称">{{ assetInfo.name }}</el-descriptions-item>
            <el-descriptions-item label="资产类别">{{ assetInfo.category_name }}</el-descriptions-item>
            <el-descriptions-item label="当前位置">{{ assetInfo.location_name }}</el-descriptions-item>
            <el-descriptions-item label="型号">{{ assetInfo.model }}</el-descriptions-item>
            <el-descriptions-item label="品牌">{{ assetInfo.brand }}</el-descriptions-item>
            <el-descriptions-item label="序列号">{{ assetInfo.serial_number }}</el-descriptions-item>
            <el-descriptions-item label="财务编码">{{ assetInfo.financial_code }}</el-descriptions-item>
            <el-descriptions-item label="规格参数">{{ assetInfo.specifications || '无' }}</el-descriptions-item>
            <el-descriptions-item label="购买日期">{{ assetInfo.purchase_date || '无' }}</el-descriptions-item>
            <el-descriptions-item label="当前状态" :span="2">
                <el-tag :type="assetInfo.status === '0' ? 'success' : 'warning'">
                    {{ assetInfo.status === '0' ? '在库' : '已领用' }}
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
                    <el-form-item label="领用人" prop="owner">
                        <el-input v-model="formData.owner" placeholder="请输入领用人：工号-姓名" style="width: 200px;" />
                    </el-form-item>
                </el-col>
                <el-col :span="12">
                    <el-form-item label="领用时间" prop="updated_at">
                        <el-date-picker v-model="formData.updated_at" type="datetime" placeholder="请选择日期"
                            style="width: 200px;" />
                    </el-form-item>
                </el-col>
                <el-col :span="12">
                    <el-form-item label="备注信息" prop="remarks">
                        <el-input v-model="formData.remarks" placeholder="请输入备注信息" style="width: 200px;" />
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
import { GetAssetLocationTree, GetAssetDepartmentTree, AssetAllocation } from "@/api/assets"

const emits = defineEmits(["success"])
const dialogVisible = ref(false)
const assetInfo = reactive({})
const formRef = ref(null)
const initForm = {
    id: null,
    location_id: null,
    department_id: null,
    owner: null,
    updated_at: null,
    remarks: null
}
const formData = reactive({})
const locationData = ref([])
const departmentData = ref([])
const files = ref([])
const formRules = reactive({
    location_id: [{ required: true, message: '请选择存放位置', trigger: 'blur' }],
    department_id: [{ required: true, message: '请选择使用部门', trigger: 'blur' }],
    owner: [{ required: true, message: '请输入使用人', trigger: 'blur' }],
})

function handleChange(file, fileList) {
    files.value = fileList;
}

function handleRemove(file, fileList) {
    files.value = fileList;
}

function handlePreview(file) {
    // 创建图片预览对话框
    const img = new Image();
    img.src = file.url;

    // 创建预览窗口
    const previewWindow = window.open('', '_blank', 'width=800,height=600,scrollbars=yes,resizable=yes');
    previewWindow.document.write(`
        <html>
            <head><title>图片预览</title></head>
            <body style="margin:0;padding:20px;text-align:center;background:#f5f5f5;">
                <img src="${file.url}" style="max-width:100%;max-height:100%;object-fit:contain;" alt="预览图片" />
            </body>
        </html>
    `);
    previewWindow.document.close();
}

async function handleSubmit() {
    formData.id = assetInfo.id
    try {
        await formRef.value.validate()
    } catch (err) {
        console.log("表单验证失败")
        return false
    }

    // 构建form表单，携带图片上传
    const formDataToSend = new FormData();
    for (let key in formData) {
        console.log(formData[key])
        if (formData[key] !== null) {
            formDataToSend.append(key, formData[key])
        }
    }

    // 添加多张图片文件
    files.value.forEach((file, index) => {
        if (file.raw) {
            // 新上传的图片文件
            formDataToSend.append(`files`, file.raw);
        }
    });

    try {
        await AssetAllocation(formDataToSend)
        dialogVisible.value = false
    } catch (err) {
        console.log("更新资产失败")
        return false
    }
    emits("success")
}

async function show(asset) {
    dialogVisible.value = true
    Object.assign(formData, JSON.parse(JSON.stringify(initForm)))
    Object.assign(assetInfo, JSON.parse(JSON.stringify(asset)))

    // 图片上传组件只用于上传新图片，不预加载现有图片
    files.value = []

    try {
        locationData.value = await GetAssetLocationTree()
        departmentData.value = await GetAssetDepartmentTree()
    } catch (err) {
        console.log("获取位置或部门失败")
        return false
    }
}

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
    width: 80px;
    height: 80px;
    border-radius: 4px;
    cursor: pointer;
}
</style>

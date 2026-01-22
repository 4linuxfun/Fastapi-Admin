<template>
    <el-dialog v-model="dialogVisible" title="报废" width="50%">
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
                    <el-image 
                        v-for="(image, index) in assetInfo.image_urls" 
                        :key="index"
                        :src="image" 
                        :preview-src-list="assetInfo.image_urls"
                        :initial-index="index"
                        fit="cover"
                        class="asset-image"
                    />
                </div>
                <span v-else>无</span>
            </el-descriptions-item>
        </el-descriptions>
        <el-form :model="formData" inline style="margin-top: 20px;" :rules="formRules" ref="formRef" label-width="80px">
            <el-form-item label="存放位置" prop="location_id">
                <el-tree-select v-model="formData.location_id" :data="locationData" :render-after-expand="false"
                    :props="{ label: 'name' }" value-key="id" check-strictly style="width: 200px;" />
            </el-form-item>
            <el-form-item label="报废原因" prop="remarks">
                <el-input v-model="formData.remarks" />
            </el-form-item>
            <el-form-item label="图片上传" prop="image">
                <el-upload ref="upload" :v-model:file-list="files" action="#" :auto-upload="false"
                    :on-change="handleChange" :on-preview="handlePreview" :on-remove="handleRemove"
                    list-type="picture-card" multiple accept="image/*">
                    <el-icon><Plus /></el-icon>
                </el-upload>
            </el-form-item>
        </el-form>
        <template #footer>
            <el-row justify="center">
                <el-button type="danger" @click="dialogVisible = false">取消</el-button>
                <el-button type="primary" @click="handleSubmit">提交</el-button>
            </el-row>
        </template>
    </el-dialog>
</template>

<script setup>
import { ref, reactive } from "vue"
import { Plus } from '@element-plus/icons-vue'
import { GetAssetLocationTree, AssetDisposal } from "@/api/assets"

const emits = defineEmits(['success'])
const dialogVisible = ref(false)
const assetInfo = reactive({})
const formRef = ref(null)
const initForm = {
    id: null,
    location_id: null,
    remarks: '故障',
    files: null,
}
const formData = reactive({})
const locationData = ref([])
const files = ref([])
const formRules = reactive({
    location_id: [{ required: true, message: '请选择存放位置', trigger: 'blur' }],
})

function handleChange(file, fileList) {
    files.value = fileList;
}

function handleRemove(file, fileList) {
    files.value = fileList;
}

function handlePreview(file) {
    window.open(file.url, '_blank');
}

async function handleSubmit() {
    formData.id = assetInfo.id
    try {
        await formRef.value.validate()
    } catch (err) {
        console.log("表单验证失败")
        return false
    }

    const formDataToSend = new FormData();
    for (let key in formData) {
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
        await AssetDisposal(formDataToSend)
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
    } catch (err) {
        console.log("获取位置失败")
        return false
    }
}

defineExpose({
    show,
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

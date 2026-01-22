<!-- 资产录入和编辑功能页面，只能修改资产信息，不能修改资产状态、使用人 -->
<template>
    <el-dialog v-model="visible" :title="title" destroy-on-close>
        <el-form :model="formData" v-loading="loading" :rules="formRules" ref="formRef" label-width="80px">
            <el-alert v-if="!isEdit && !isFromInventory" title="资产编号后端自动生成" type="info" style="margin-bottom: 10px;" />
            <el-alert v-if="!isEdit && isFromInventory" title="通过盘点新增资产，资产编号后端自动生成" type="warning" style="margin-bottom: 10px;" />
            <el-form-item v-if="isEdit" label="资产编号" prop="asset_code">
                <el-input v-model="formData.asset_code" disabled />
            </el-form-item>
            <el-form-item label="资产名称" prop="name">
                <el-input v-model="formData.name" placeholder="请输入资产名称" />
            </el-form-item>
            <el-form-item label="资产类别" prop="category_id">
                <el-tree-select v-model="formData.category_id" :data="categoryData" :render-after-expand="false"
                    :props="{ label: 'name' }" value-key="id" check-strictly />
            </el-form-item>
            <el-form-item label="资产型号" prop="model">
                <el-input v-model="formData.model" placeholder="请输入资产型号" />
            </el-form-item>
            <el-form-item label="品牌" prop="brand">
                <el-input v-model="formData.brand" placeholder="请输入品牌" />
            </el-form-item>
            <el-form-item label="序列号" prop="serial_number">
                <el-input v-model="formData.serial_number" placeholder="请输入序列号" />
            </el-form-item>
            <el-form-item label="规格" prop="specifications">
                <el-input v-model="formData.specifications" placeholder="请输入规格" />
            </el-form-item>
            <el-form-item label="财务编码" prop="financial_code">
                <el-input v-model="formData.financial_code" placeholder="请输入财务编码" />
            </el-form-item>
            <el-form-item label="购买日期" prop="purchase_date">
                <el-date-picker v-model="formData.purchase_date" type="date" placeholder="选择日期" style="width: 100%;" />
            </el-form-item>
            <!-- <el-form-item label="购买价格" prop="purchase_price">
                <el-input v-model="formData.purchase_price" placeholder="请输入购买价格" />
            </el-form-item> -->
            <el-form-item label="存放位置" prop="location_id">
                <el-tree-select v-model="formData.location_id" :data="locationData" :render-after-expand="false"
                    :props="{ label: 'name' }" value-key="id" check-strictly />
            </el-form-item>
            <!-- 使用部门字段只在编辑模式下显示，录入时不显示 -->
            <el-form-item v-if="isEdit" label="使用部门" prop="department_id">
                <el-tree-select v-model="formData.department_id" :data="departmentData" :render-after-expand="false"
                    :props="{ label: 'name' }" value-key="id" check-strictly />
            </el-form-item>
            <el-form-item label="备注" prop="remarks">
                <el-input v-model="formData.remarks" :rows="2" type="textarea" placeholder="请输入备注" />
            </el-form-item>
            <el-form-item label="图片上传" prop="image">
                <el-upload ref="upload" :file-list="files" action="#" :auto-upload="false"
                    :on-change="handleChange" :on-preview="handlePreview" :on-remove="handleRemove" list-type="picture-card" multiple accept="image/*">
                    <el-icon><Plus /></el-icon>
                </el-upload>
            </el-form-item>
        </el-form>
        <el-row justify="center">
            <el-button @click="visible = false" type="danger">取消</el-button>
            <el-button v-if="formData.id" type="primary" @click="handleUpdate">更新</el-button>
            <el-button v-else type="primary" @click="handleUpdate">添加</el-button>
        </el-row>
    </el-dialog>
</template>

<script setup>
import { ref, reactive } from "vue"
import { Plus } from '@element-plus/icons-vue'
import { AssetEntry, GetAssetCategoryTree, GetAssetLocationTree, GetAssetDepartmentTree, GetAssetById, AssetUpdate, CreateInventoryRecord } from "@/api/assets"

const emits = defineEmits(["success"])
const visible = ref(false)
const title = ref("")
const isEdit = ref(false)
const formRef = ref(null)
const formData = reactive({})
const categoryData = ref([])
const locationData = ref([])
const departmentData = ref([])
const loading = ref(false)
const files = ref([])
// 盘点相关状态
const isFromInventory = ref(false)
const inventoryBatchId = ref(null)

const formRules = reactive({
    name: [{ required: true, message: '请输入资产名称', trigger: 'blur' }],
    category_id: [{ required: true, message: '请选择资产类别', trigger: 'blur' }],
    model: [{ required: true, message: '请输入资产型号', trigger: 'blur' }],
    brand: [{ required: true, message: '请输入品牌', trigger: 'blur' }],
    serial_number: [{ required: true, message: '请输入序列号', trigger: 'blur' }],
    location_id: [{ required: true, message: '请选择存放位置', trigger: 'blur' }],
})
const initAsset = {
    id: null,
    name: null,
    asset_code: null,
    category_id: null,
    model: null,
    brand: null,
    serial_number: null,
    specifications: null,
    financial_code: null,
    purchase_date: null,
    purchase_price: null,
    location: null,
    owner: null,
    location_id: null,
    department_id: null,
    status: null,
    remarks: null,
}

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

async function handleUpdate() {
    try {
        await formRef.value.validate()
    } catch (err) {
        console.log("表单验证失败")
        return false
    }
    // 构建form表单，携带图片上传
    const formDataToSend = new FormData();
    // formDataToSend.append("id", formData.id);
    // formDataToSend.append("name", formData.name);
    // formDataToSend.append("asset_code", formData.asset_code);
    // formDataToSend.append("category_id", formData.category_id);
    // formDataToSend.append("model", formData.model);
    // formDataToSend.append("brand", formData.brand);
    // formDataToSend.append("serial_number", formData.serial_number);
    // formDataToSend.append("specifications", formData.specifications);
    // formDataToSend.append("financial_code", formData.financial_code);
    // formDataToSend.append("purchase_date", formData.purchase_date);
    // formDataToSend.append("location_id", formData.location_id);
    // if(formData.remarks !== null){
    //     formDataToSend.append("remarks", formData.remarks);
    // }
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
        } else if (file.url) {
            // 已存在的图片URL，需要保留
            formDataToSend.append(`existing_images`, file.url);
        }
    });
    loading.value = true
    try {
        if (isEdit.value) {
            // 编辑
            await AssetUpdate(formDataToSend)
        } else {
            // 新增
            if (isFromInventory.value && inventoryBatchId.value) {
                // 通过盘点新增资产，使用盘点记录接口
                formDataToSend.append('batch_id', inventoryBatchId.value)
                formDataToSend.append('action_type', 'NEW_ASSET')
                await CreateInventoryRecord(formDataToSend)
            } else {
                // 普通资产新增
                await AssetEntry(formDataToSend)
            }
        }
    } catch (err) {
        console.log("上传失败", err)
        return false
    } finally {
        loading.value = false
    }
    visible.value = false
    emits("success")
}

async function add() {
    visible.value = true
    title.value = "资产录入"
    isEdit.value = false
    isFromInventory.value = false
    inventoryBatchId.value = null
    Object.assign(formData, initAsset)
    formData.status = 0
    files.value = [] // 清空图片列表
    try {
        categoryData.value = await GetAssetCategoryTree()
        locationData.value = await GetAssetLocationTree()
        // 录入模式下不需要获取部门数据，因为不显示使用部门字段
    } catch (err) {
        console.log('获取资产类别失败。。。', err)
        return false
    }
}

// 从盘点页面新增资产
async function addWithBatch(batchId) {
    visible.value = true
    title.value = "盘点新增资产"
    isEdit.value = false
    isFromInventory.value = true
    inventoryBatchId.value = batchId
    Object.assign(formData, initAsset)
    formData.status = 0
    files.value = [] // 清空图片列表
    try {
        categoryData.value = await GetAssetCategoryTree()
        locationData.value = await GetAssetLocationTree()
        // 录入模式下不需要获取部门数据，因为不显示使用部门字段
    } catch (err) {
        console.log('获取资产类别失败。。。', err)
        return false
    }
}

async function edit(assetId) {
    visible.value = true
    title.value = "更新资产"
    Object.assign(formData, initAsset)
    loading.value = true
    try {
        const res = await GetAssetById(assetId)
        Object.assign(formData, res)
        
        // 处理图片数据
        if (res.image_urls && Array.isArray(res.image_urls)) {
            files.value = res.image_urls.map((url, index) => ({
                name: `image_${index + 1}.jpg`,
                url: url,
                uid: Date.now() + index,
                status: 'success'
            }))
        } else {
            files.value = []
        }
        
        isEdit.value = true
        categoryData.value = await GetAssetCategoryTree()
        locationData.value = await GetAssetLocationTree()
        departmentData.value = await GetAssetDepartmentTree()
    } catch (err) {
        console.log('获取资产类别失败。。。', err)
        return false
    }
    loading.value = false
}

defineExpose({
    add,
    edit,
    addWithBatch
})
</script>

<style scoped></style>

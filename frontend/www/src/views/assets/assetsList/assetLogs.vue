<template>
    <el-dialog v-model="visible" title="资产历史记录" width="50%" :close-on-click-modal="false">
        <el-form inline :model="formData">
            <el-form-item label="开始时间">
                <el-date-picker v-model="formData.start" type="date" placeholder="选择日期时间" value-format="YYYY-MM-DD"
                    style="width: 200px;">
                </el-date-picker>
            </el-form-item>
            <el-form-item label="结束时间" prop="name">
                <el-date-picker v-model="formData.end" type="date" placeholder="选择日期时间" value-format="YYYY-MM-DD"
                    style="width: 200px;">
                </el-date-picker>
            </el-form-item>
            <el-form-item>
                <el-button type="primary" @click="handleSearch">查询</el-button>
            </el-form-item>
        </el-form>
        <el-timeline>
            <el-timeline-item v-for="(log, index) in assetLogs" :key="index" :timestamp="log.timestamp" placement="top"
                center>
                <el-card>
                    <el-descriptions v-if="log.action === '资产录入' || log.action === '资产编辑'" :title="log.action">
                        <el-descriptions-item label="资产编号：">{{ log.details.asset_code }}</el-descriptions-item>
                        <el-descriptions-item label="资产名称：">{{ log.details.name }}</el-descriptions-item>
                        <el-descriptions-item label="资产品牌：">{{ log.details.brand }}</el-descriptions-item>
                        <el-descriptions-item label="资产型号：">{{ log.details.model }}</el-descriptions-item>
                        <el-descriptions-item label="资产序列号：">{{ log.details.serial_number }}</el-descriptions-item>
                        <el-descriptions-item label="资产类别：">{{ log.details.category }}</el-descriptions-item>
                        <el-descriptions-item label="资产位置：">{{ log.details.location }}</el-descriptions-item>
                        <el-descriptions-item label="所属部门：">{{ log.details.department || '无' }}</el-descriptions-item>
                        <el-descriptions-item label="购买日期：">{{ log.details.purchase_date }}</el-descriptions-item>
                        <el-descriptions-item label="操作人：" :span="3">{{ log.operator }}</el-descriptions-item>
                        <el-descriptions-item label="图片：" :span="3">
                            <template v-if="log.images">
                                <el-image v-for="(image, index) in log.images" :key="index" :src="image"
                                    :preview-src-list="log.images" style="width: 100px; height: 100px;">
                                </el-image>
                            </template>
                            <template v-else>无</template>
                        </el-descriptions-item>
                    </el-descriptions>
                    <el-descriptions v-if="log.action === '资产领用'" title="资产领用">
                        <el-descriptions-item label="资产名称：">{{ log.details.asset_name }}</el-descriptions-item>
                        <el-descriptions-item label="资产编号：">{{ log.details.asset_code }}</el-descriptions-item>
                        <el-descriptions-item label="资产类别：">{{ log.details.category }}</el-descriptions-item>
                        <el-descriptions-item label="领用人：">{{ log.details.owner }}</el-descriptions-item>
                        <el-descriptions-item label="使用部门：">{{ log.details.department || '无' }}</el-descriptions-item>
                        <el-descriptions-item label="使用位置：">{{ log.details.location }}</el-descriptions-item>
                        <el-descriptions-item label="备注：">{{ log.details.remarks }}</el-descriptions-item>
                        <el-descriptions-item label="领用时间：">{{ log.details.updated_at }}</el-descriptions-item>
                        <el-descriptions-item label="操作人：" :span="2">{{ log.operator }}</el-descriptions-item>
                        <el-descriptions-item label="图片：" :span="3">
                            <template v-if="log.images">
                                <el-image v-for="(image, index) in log.images" :key="index" :src="image"
                                    :preview-src-list="log.images" style="width: 100px; height: 100px;">
                                </el-image>
                            </template>
                            <template v-else>无</template>
                        </el-descriptions-item>
                    </el-descriptions>
                    <el-descriptions v-if="log.action === '资产退回'" title="资产退回">
                        <el-descriptions-item label="资产名称：">{{ log.details.asset_name }}</el-descriptions-item>
                        <el-descriptions-item label="资产编号：">{{ log.details.asset_code }}</el-descriptions-item>
                        <el-descriptions-item label="资产类别：">{{ log.details.category }}</el-descriptions-item>
                        <el-descriptions-item label="原领用人：">{{ log.details.previous_owner }}</el-descriptions-item>
                        <el-descriptions-item label="原使用部门：">{{ log.details.previous_department_full_path || '无' }}</el-descriptions-item>
                        <el-descriptions-item label="退回后存放位置：">{{ log.details.location }}</el-descriptions-item>
                        <el-descriptions-item label="退回时间：">{{ log.timestamp }}</el-descriptions-item>
                        <el-descriptions-item label="操作人：">{{ log.operator }}</el-descriptions-item>
                        <el-descriptions-item label="图片：" :span="3">
                            <template v-if="log.images">
                                <el-image v-for="(image, index) in log.images" :key="index" :src="image"
                                    :preview-src-list="log.images" style="width: 100px; height: 100px;">
                                </el-image>
                            </template>
                            <template v-else>无</template>
                        </el-descriptions-item>
                    </el-descriptions>

                    <el-descriptions v-if="log.action === '资产报废'" title="资产报废">
                        <el-descriptions-item label="资产名称：">{{ log.details.asset_name }}</el-descriptions-item>
                        <el-descriptions-item label="资产编号：">{{ log.details.asset_code }}</el-descriptions-item>
                        <el-descriptions-item label="资产类别：">{{ log.details.category }}</el-descriptions-item>
                        <el-descriptions-item label="报废存放位置：">{{ log.details.location }}</el-descriptions-item>
                        <el-descriptions-item label="报废原因：">{{ log.details.remarks }}</el-descriptions-item>
                        <el-descriptions-item label="报废时间：">{{ log.timestamp }}</el-descriptions-item>
                        <el-descriptions-item label="操作人：">{{ log.operator }}</el-descriptions-item>
                        <el-descriptions-item label="图片：" :span="3">
                            <template v-if="log.images">
                                <el-image v-for="(image, index) in log.images" :key="index" :src="image"
                                    :preview-src-list="log.images" style="width: 100px; height: 100px;">
                                </el-image>
                            </template>
                            <template v-else>无</template>
                        </el-descriptions-item>
                    </el-descriptions>
                    
                    <el-descriptions v-if="log.action === '资产转移'" title="资产转移">
                        <el-descriptions-item label="资产名称：">{{ log.details.asset_name }}</el-descriptions-item>
                        <el-descriptions-item label="资产编号：">{{ log.details.asset_code }}</el-descriptions-item>
                        <el-descriptions-item label="资产类别：">{{ log.details.category }}</el-descriptions-item>
                        <el-descriptions-item label="原使用人：">{{ log.details.previous_owner || '无' }}</el-descriptions-item>
                        <el-descriptions-item label="原使用部门：">{{ log.details.previous_department_full_path || '无' }}</el-descriptions-item>
                        <el-descriptions-item label="原存放位置：">{{ log.details.previous_location || '无' }}</el-descriptions-item>
                        <el-descriptions-item label="新使用人：">{{ log.details.owner }}</el-descriptions-item>
                        <el-descriptions-item label="新使用部门：">{{ log.details.department || '无' }}</el-descriptions-item>
                        <el-descriptions-item label="新存放位置：">{{ log.details.location }}</el-descriptions-item>
                        <el-descriptions-item label="转移时间：">{{ log.timestamp }}</el-descriptions-item>
                        <el-descriptions-item label="备注：">{{ log.details.remarks || '无' }}</el-descriptions-item>
                        <el-descriptions-item label="操作人：">{{ log.operator }}</el-descriptions-item>
                        <el-descriptions-item label="图片：" :span="3">
                            <template v-if="log.images">
                                <el-image v-for="(image, index) in log.images" :key="index" :src="image"
                                    :preview-src-list="log.images" style="width: 100px; height: 100px;">
                                </el-image>
                            </template>
                            <template v-else>无</template>
                        </el-descriptions-item>
                    </el-descriptions>
                </el-card>
            </el-timeline-item>
        </el-timeline>
    </el-dialog>
</template>

<script setup>
import { ref, reactive } from 'vue';
import dayjs from 'dayjs';
import { ElMessage } from 'element-plus';
import { GetAssetLogs } from '@/api/assets';

const visible = ref(false);
const logId = ref(null)
// 示例数据
const assetLogs = ref([])
const formData = reactive({
    start: '',
    end: ''
})

async function handleSearch() {
    // 处理查询逻辑
    try {
        const logs = await GetAssetLogs(logId.value, formData);
        if (logs.length === 0) {
            ElMessage.info('未找到相关记录');
        }

        assetLogs.value = logs.map(log => {
            try {
                // 尝试将 details 字段解析为 JSON 对象（如果后端返回的是字符串）
                if (typeof log.details === 'string') {
                    log.details = JSON.parse(log.details);
                }
                if (log.images && typeof log.images === 'string') {
                    log.images = JSON.parse(log.images);
                }
                // 使用后端返回的timestamp作为时间戳
                log.timestamp = log.timestamp ? dayjs(log.timestamp).format('YYYY-MM-DD HH:mm:ss') : '';
            } catch (parseErr) {
                console.error("解析字段失败:", parseErr);
                // 如果解析失败，可以设置一个默认值或保留原字符串
                if (typeof log.details === 'string') {
                    log.details = {};
                }
            }
            return log;
        });
    } catch (err) {
        console.error("获取资产日志失败", err);
        ElMessage.error('获取资产日志失败');
        return false
    }
}

async function show(id) {
    visible.value = true
    logId.value = id
    assetLogs.value = []
    formData.start = dayjs().subtract(1, 'month').format('YYYY-MM-DD')// 设置默认开始时间为一个月前
    formData.end = dayjs().format('YYYY-MM-DD') // 设置默认结束时间为当前时间
    await handleSearch();
}

defineExpose({
    show
})
</script>

<style scoped>
/* 自定义样式 */
.el-timeline {
    margin-top: 20px;
}
</style>
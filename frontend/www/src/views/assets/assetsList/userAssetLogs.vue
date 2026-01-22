<template>
    <el-dialog v-model="visible" title="用户资产领用退回记录" width="50%" :close-on-click-modal="false">
        <el-form inline :model="formData">
            <el-form-item label="用户名">
                <el-input v-model="formData.username" placeholder="请输入用户名" style="width: 200px;"></el-input>
            </el-form-item>
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
                    <el-descriptions v-if="log.action === '资产领用'" title="资产领用">
                        <el-descriptions-item label="资产名称：">{{ log.details.asset_name }}</el-descriptions-item>
                        <el-descriptions-item label="资产编号：">{{ log.details.asset_code }}</el-descriptions-item>
                        <el-descriptions-item label="资产类别：">{{ log.details.category }}</el-descriptions-item>
                        <el-descriptions-item label="领用人：">{{ log.details.owner }}</el-descriptions-item>
                        <el-descriptions-item label="使用位置：">{{ log.details.location }}</el-descriptions-item>
                        <el-descriptions-item label="具体位置：">{{ log.details.remarks }}</el-descriptions-item>
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
                        <el-descriptions-item label="退回后存放位置：">{{ log.details.location }}</el-descriptions-item>
                        <el-descriptions-item label="退回时间：">{{ log.details.updated_at }}</el-descriptions-item>
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
import { GetUserAssetLogs } from '@/api/assets';

const visible = ref(false);
// 示例数据
const assetLogs = ref([])
const formData = reactive({
    username: '',
    start: '',
    end: ''
})

async function handleSearch() {
    if (!formData.username) {
        ElMessage.warning('请输入用户名');
        return;
    }

    // 处理查询逻辑
    try {
        const response = await GetUserAssetLogs(formData.username, {
            start: formData.start,
            end: formData.end
        });

        if (response.length === 0) {
            ElMessage.info('未找到相关记录');
        }

        assetLogs.value = response.map(log => {
            try {
                // 尝试将 details 字段解析为 JSON 对象（如果后端返回的是字符串）
                if (typeof log.details === 'string') {
                    log.details = JSON.parse(log.details);
                }
                if (log.images && typeof log.images === 'string') {
                    log.images = JSON.parse(log.images);
                }
                // 使用后端返回的timestamp或created_at作为时间戳
                log.timestamp = log.timestamp ? dayjs(log.timestamp).format('YYYY-MM-DD HH:mm:ss') :
                    (log.created_at ? dayjs(log.created_at).format('YYYY-MM-DD HH:mm:ss') : '');
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
        console.error("获取用户资产日志失败", err);
        ElMessage.error('获取用户资产日志失败');
    }
}

async function show() {
    visible.value = true
    assetLogs.value = []
    formData.username = ''
    formData.start = dayjs().subtract(1, 'month').format('YYYY-MM-DD')// 设置默认开始时间为一个月前
    formData.end = dayjs().format('YYYY-MM-DD') // 设置默认结束时间为当前时间
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
<template>
  <el-descriptions border>
    <el-descriptions-item label="任务ID">{{ props.job.id }}</el-descriptions-item>
    <el-descriptions-item label="任务名称">{{ props.job.name }}</el-descriptions-item>
    <el-descriptions-item label="类型">{{ props.job.trigger }}</el-descriptions-item>
    <el-descriptions-item label="执行命令">{{ props.job.command }}</el-descriptions-item>
    <template v-if="props.job.trigger === 'cron'">
      <el-descriptions-item label="Cron规则">{{ props.job.trigger_args.cron }}</el-descriptions-item>
      <el-descriptions-item label="开始时间">{{ props.job.trigger_args.start_date }}</el-descriptions-item>
      <el-descriptions-item label="结束时间">{{ props.job.trigger_args.end_date }}</el-descriptions-item>
    </template>
    <template v-else-if="props.job.trigger === 'date'">
      <el-descriptions-item label="执行时间">{{ props.job.trigger_args }}</el-descriptions-item>
    </template>

  </el-descriptions>
  <el-table :data="tableData" border style="margin-top: 20px;">
    <el-table-column type="index" label="#"/>
    <el-table-column label="执行时间" prop="start_time"/>
    <el-table-column label="执行状态">
      <template #default="scope">
        <el-tag effect="dark" :type="scope.row.status === 0 ? 'success':'danger'">
          {{ scope.row.status === 0 ? '正常' : '失败' }}
        </el-tag>
      </template>
    </el-table-column>
    <el-table-column label="操作">
      <template #default="scope">
        <el-button size="small" @click="showLog(scope.row.log)">详情</el-button>
      </template>
    </el-table-column>
  </el-table>

  <el-dialog v-model="logDialog" title="任务日志" destroy-on-close>
    <log-detail :log="selectLog"/>
  </el-dialog>

  <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total" background
                 layout="total,prev,pager,next,sizes,jumper"
                 style="margin-top: 10px;"
  />
</template>

<script setup>
  import {ref, reactive} from 'vue'
  import usePagination from '@/composables/usePagination'
  import LogDetail from '@/views/jobs/JobManage/LogDetail.vue'

  const props = defineProps(['job'])
  const selectLog = reactive({})
  const logDialog = ref(false)

  const searchForm = {
    job_id: props.job.id,
  }
  const {
    search,
    tableData,
    currentPage,
    pageSize,
    orderModel,
    total,
    freshCurrentPage,
    handleSearch
  } = usePagination('/api/jobs/logs', searchForm, 'desc')

  function showLog(log) {
    logDialog.value = true
    Object.assign(selectLog, log)
  }
</script>

<style scoped>

</style>
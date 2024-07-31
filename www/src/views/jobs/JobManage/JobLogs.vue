<template>
  <el-descriptions border>
    <el-descriptions-item label="任务ID">{{ props.job.id }}</el-descriptions-item>
    <el-descriptions-item label="任务名称">{{ props.job.name }}</el-descriptions-item>
    <el-descriptions-item label="类型">{{ props.job.trigger }}</el-descriptions-item>
    <el-descriptions-item label="执行模块">{{ props.job.ansible_args.module }}</el-descriptions-item>
    <el-descriptions-item label="模块参数">{{ props.job.ansible_args.module_args }}</el-descriptions-item>
    <template v-if="props.job.trigger === 'cron'">
      <el-descriptions-item label="Cron规则">{{ props.job.trigger_args.cron }}</el-descriptions-item>
      <el-descriptions-item label="开始时间">{{ props.job.trigger_args.start_date }}</el-descriptions-item>
      <el-descriptions-item label="结束时间">{{ props.job.trigger_args.end_date }}</el-descriptions-item>
    </template>
    <template v-else-if="props.job.trigger === 'date'">
      <el-descriptions-item label="执行时间">{{ props.job.trigger_args.run_date }}</el-descriptions-item>
    </template>

  </el-descriptions>
  <el-table :data="tableData" border style="margin-top: 20px;">
    <el-table-column type="index" label="#"/>
    <el-table-column label="执行时间" prop="start_time"/>
    <el-table-column label="执行状态">
      <template #default="scope">
        <el-tag effect="dark" :type="statsCheck(scope.row.stats) ? 'danger':'success'">
          {{ statsCheck(scope.row.stats) ? '失败' : '成功' }}
        </el-tag>
      </template>
    </el-table-column>
    <el-table-column label="操作">
      <template #default="scope">
        <el-button size="small" @click="showLog(scope.row)">详情</el-button>
      </template>
    </el-table-column>
  </el-table>

  <log-detail ref="logDetailRef"/>

  <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total" background
                 layout="total,prev,pager,next,sizes,jumper"
                 style="margin-top: 10px;"
  />
</template>

<script setup>
  import {ref, reactive, onMounted} from 'vue'
  import usePagination from '@/composables/usePagination'
  import LogDetail from '@/views/jobs/JobManage/LogDetail.vue'

  const props = defineProps(['job'])
  const selectLog = reactive({})
  const logDialog = ref(false)
  const logDetailRef = ref(null)

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

  // 调用子组件现实日志详情
  function showLog(log) {
    console.log(log)
    logDetailRef.value.show(log)
  }

  // 状态检查，看有无failure 字段
  function statsCheck(stats) {
    console.log(stats)
    let log_stats = JSON.parse(stats)
    console.log(log_stats.failure)
    console.log(log_stats.ok)
    return log_stats.failure === null
  }

  onMounted(() => {
    handleSearch()
  })
</script>

<style scoped>

</style>
<template>
  <el-row>
    <el-form v-model="search" inline>
      <el-form-item label="任务名">
        <el-input v-model="search.job_name"/>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button type="primary" @click="handleEdit(null)">新建</el-button>
      </el-form-item>
    </el-form>
  </el-row>
  <el-table :data="tableData" border>
    <el-table-column type="index" label="#"/>
    <el-table-column label="任务ID" prop="id"/>
    <el-table-column label="任务名" prop="name"/>
    <el-table-column label="类型">
      <template #default="scope">
        <el-tag v-if="scope.row.trigger === 'cron'" type="success">Cron</el-tag>
        <el-tag v-else-if="scope.row.trigger === 'date'" type="info">Date</el-tag>
        <el-tag v-else type="warning">Interval</el-tag>
      </template>
    </el-table-column>
    <el-table-column label="执行命令" prop="command"/>
    <el-table-column label="状态">
      <template #default="scope">
        <el-switch v-model="scope.row.status" active-value="running" inactive-value="stop"
                   @change="handleStatus(scope.row.id)"/>
      </template>
    </el-table-column>
    <el-table-column label="操作">
      <template #default="scope">
        <el-button type="primary" size="small" @click="handleEdit(scope.row)">编辑</el-button>
        <el-button type="primary" size="small" @click="handleLogs(scope.row.id)">日志</el-button>
        <el-button type="danger" size="small" @click="handleDel(scope.row)">删除</el-button>
      </template>
    </el-table-column>
  </el-table>

  <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total" background
                 layout="total,prev,pager,next,sizes,jumper"
                 style="margin-top: 10px;"
  />

  <el-dialog v-model="addDrawer" title="任务编辑" destroy-on-close>
    <add-job v-model:visible="addDrawer" :job="jobInfo"/>
  </el-dialog>

  <el-dialog v-model="logDrawer" title="任务记录" destroy-on-close>
    <add-job v-model:visible="logDrawer" :job="jobId"/>
  </el-dialog>
</template>

<script>
  export default {
    name: '任务管理'
  }
</script>

<script setup>

  import {ref, onMounted, watch} from 'vue'
  import AddJob from '@/views/jobs/JobManage/AddJob.vue'
  import {DelJob, GetJobList, SwitchJob} from '@/api/jobs'
  import {ConfirmDel} from '@/utils/request'
  import usePagination from '@/composables/usePagination'

  const addDrawer = ref(false)
  const logDrawer = ref(false)
  let jobInfo = null

  const searchForm = {
    job_name: null,
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
  } = usePagination('/api/jobs/search', searchForm)

  function handleEdit(job) {
    jobInfo = job
    addDrawer.value = true
  }

  function handleStatus(jobId) {
    SwitchJob(jobId).then(() => {
      freshCurrentPage()
    }).catch(error=>{
      freshCurrentPage()
    })
  }

  function handleDel(job) {
    ConfirmDel('是否确定要删除任务：' + job.name, DelJob, job.id)
  }

  function handleLogs(jobId) {
    logDrawer.value = true
  }

  watch(addDrawer, (newValue) => {
    if (newValue === false) {
      freshCurrentPage()
    }

  })
  onMounted(() => {
    handleSearch()
  })
</script>

<style scoped>

</style>
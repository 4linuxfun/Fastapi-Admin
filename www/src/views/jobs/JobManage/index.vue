<template>
  <el-row>
    <el-form v-model="search" inline>
      <el-form-item label="任务名">
        <el-input v-model="search.job_id"/>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button type="primary" @click="handleEdit(null)">新建</el-button>
      </el-form-item>
    </el-form>
  </el-row>
  <el-table :data="tableData" border>
    <el-table-column type="index" label="#"/>
    <el-table-column label="任务ID" prop="job_id"/>
    <el-table-column label="执行命令" prop="command"/>
    <el-table-column label="定时器(分 时 日 月 周)">
      <template #default="scope">
        <span>{{ scope.row.cron_args.cron }}</span>
      </template>
    </el-table-column>
    <el-table-column label="开始时间">
      <template #default="scope">
        <span>{{ scope.row.cron_args.start_date }}</span>
      </template>
    </el-table-column>
    <el-table-column label="结束时间">
      <template #default="scope">
        <span>{{ scope.row.cron_args.end_date }}</span>
      </template>
    </el-table-column>
    <el-table-column label="状态" prop="status">
      <template #default="scope">
        <el-switch v-model="scope.row.status" active-value="running" inactive-value="stop"
                   @change="handleStatus(scope.row)"/>
      </template>
    </el-table-column>
    <el-table-column label="操作">
      <template #default="scope">
        <el-button type="primary" size="small" @click="handleEdit(scope.row)">编辑</el-button>
        <el-button type="danger" size="small" @click="handleDel(scope.row.job_id)">删除</el-button>
      </template>
    </el-table-column>
  </el-table>

   <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total" background
                   layout="total,prev,pager,next,sizes,jumper"
                   style="margin-top: 10px;"
    />

  <el-drawer v-model="addDrawer" title="任务编辑" destroy-on-close>
    <add-job v-model:visible="addDrawer" :job="jobInfo"/>
  </el-drawer>
</template>

<script>
  export default {
    name: '任务管理'
  }
</script>

<script setup>

  import {ref, onMounted, watch} from 'vue'
  import AddJob from '@/views/jobs/JobManage/AddJob.vue'
  import {DelJob, GetJobList, PauseJob, ResumeJob} from '@/api/jobs'
  import {ElMessage, ElMessageBox} from 'element-plus'
  import {ConfirmDel} from '@/utils/request'
  import usePagination from '@/composables/usePagination'

  const addDrawer = ref(false)
  let jobInfo = null

  const searchForm = {
    job_id: null,
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

  function handleStatus(job) {
    if (job.status === 'stop') {
      PauseJob(job.job_id)
    } else {
      ResumeJob(job.job_id)
    }
    searchJobs()
  }

  function handleDel(jobId) {
    ConfirmDel('是否确定要删除任务：' + jobId, DelJob, jobId)
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
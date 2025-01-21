<template>
  <div style="background-color:white;height: 100%;padding: 10px">
    <el-row :gutter="10">
      <el-col :span="8">
        <add-job :data="addJobData" @cancel="addDialog = false" @submit="handleSubmit"/>
      </el-col>
      <el-col :span="16">
        <el-table :data="tableData" style="width: 100%" border>
          <el-table-column label="#" type="index"/>
          <el-table-column prop="job_id" label="任务ID" width="300"/>
          <el-table-column prop="start_time" label="开始时间"/>
          <el-table-column prop="end_time" label="结束时间"/>
          <el-table-column label="详情">
            <template #default="scope">
              <el-button type="primary" @click="logDetailRef.show(scope.row)">查看日志</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total" background
                       layout="total,prev,pager,next,sizes,jumper"
                       style="margin-top: 10px;"
        />
      </el-col>
    </el-row>
  </div>

  <log-drawer ref="logDrawerRef"/>
  <log-detail ref="logDetailRef"/>
</template>

<script>
  export default {
    name: '任务执行'
  }
</script>

<script setup>
  import {ref, onMounted} from 'vue'
  import AddJob from '@/views/jobs/components/AddJob.vue'
  import LogDrawer from '@/views/jobs/Execute/LogDrawer.vue'
  import {PostNewCronJob} from '@/api/jobs.js'
  import usePagination from '@/composables/usePagination.js'
  import LogDetail from '@/views/jobs/JobManage/LogDetail.vue'

  const addJobData = ref(null)
  const logDrawerRef = ref(null)
  const logDetailRef = ref(null)
  const searchForm = {
    type: 1
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
  } = usePagination('/api/jobs/logs', searchForm)

  async function handleSubmit(job) {
    console.log(job)
    let jobId = await PostNewCronJob(job)
    console.log(jobId)
    logDrawerRef.value.show(jobId)
  }

  onMounted(() => {
    handleSearch()
  })


</script>
<style scoped>

</style>
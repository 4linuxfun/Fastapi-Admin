<template>
  <el-row>
    <el-form v-model="search" inline>
      <el-form-item label="任务名">
        <el-input v-model.trim="search.job_name" clearable/>
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
        <el-tag effect="dark" :type="scope.row.trigger === 'cron'? 'success':'info'">
          {{ scope.row.trigger === 'cron' ? 'Cron' : 'Date' }}
        </el-tag>
      </template>
    </el-table-column>
    <!--    <el-table-column label="执行方式">-->
    <!--      <template #default="scope">-->
    <!--        <span-->
    <!--            v-if="scope.row.ansible_args.module !== null">模块：{{ scope.row.ansible_args.module }}，参数：{{ scope.row.ansible_args.module_args }}</span>-->
    <!--        <span v-else>脚本：{{ scope.row.ansible_args.playbook }}</span>-->
    <!--      </template>-->
    <!--    </el-table-column>-->
    <el-table-column label=" 状态">
      <template #default="scope">
        <el-switch v-model="scope.row.status" active-value="1" inactive-value="0"
                   @change="handleStatus(scope.row.id,scope.row.status)"/>
      </template>
    </el-table-column>
    <el-table-column label="操作">
      <template #default="scope">
        <el-button type="primary" size="small" @click="handleEdit(scope.row)">编辑</el-button>
        <el-button type="primary" size="small" @click="handleLogs(scope.row)">日志</el-button>
        <el-button type="danger" size="small" @click="handleDel(scope.row)">删除</el-button>
      </template>
    </el-table-column>
  </el-table>

  <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total" background
                 layout="total,prev,pager,next,sizes,jumper"
                 style="margin-top: 10px;"
  />


  <el-dialog v-model="addDialog" :title="addJobTitle" width="50%" destroy-on-close>
    <add-job :data="addJobData" dialog @cancel="addDialog = false" @submit="handleAdd"/>
  </el-dialog>

  <el-dialog v-model="logDrawer" title="任务日志" destroy-on-close>
    <job-logs :job="jobInfo"/>
  </el-dialog>
</template>

<script>
  export default {
    name: '任务管理'
  }
</script>

<script setup>

  import {ref, onMounted} from 'vue'
  import JobLogs from '@/views/jobs/JobManage/JobLogs.vue'
  import {DelJob, PostNewCronJob, PutCronJob, SwitchJob} from '@/api/jobs'
  import {ConfirmDel} from '@/utils/request'
  import usePagination from '@/composables/usePagination'
  import AddJob from '@/views/jobs/components/AddJob.vue'
  import {ElNotification} from 'element-plus'

  const logDrawer = ref(false)
  const addDialog = ref(false)
  const addJobData = ref(null)
  const addJobTitle = ref('')
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
    if (job === null) {
      addJobTitle.value = '新建任务'
      addDialog.value = true
      addJobData.value = null
    } else {
      console.log(job)
      addJobTitle.value = '编辑任务'
      addDialog.value = true
      addJobData.value = job
    }
  }

  function handleStatus(jobId, status) {
    SwitchJob(jobId, status).then(() => {
      freshCurrentPage()
    }).catch(error => {
      freshCurrentPage()
    })
  }

  async function handleDel(job) {
    try {
      await ConfirmDel('是否确定要删除任务：' + job.name, DelJob, job.id)
    } catch (e) {
      console.log(e)
    }
    await freshCurrentPage()
  }

  function handleLogs(job) {
    console.log(job)
    jobInfo = job
    logDrawer.value = true
  }

  /**
   * 确认按钮，提交任务
   * @return {Promise<void>}
   */
  async function handleAdd(addForm) {
    if (addForm.id === null) {
      try {
        await PostNewCronJob(addForm)
        ElNotification({
          title: 'success',
          message: '任务添加成功:',
          type: 'success'
        })
      } catch (error) {
        console.log(error)
      }

    } else {
      try {
        await PutCronJob(addForm)
        ElNotification({
          title: 'success',
          message: '任务修改成功:',
          type: 'success'
        })
      } catch (error) {
        console.log(error)
      }
    }
    addDialog.value = false
    freshCurrentPage()
  }

  onMounted(() => {
    handleSearch()
  })
</script>

<style scoped>

</style>
<template>
  <el-form v-model="addForm" label-position="top">
    <el-form-item label="任务名称">
      <el-input v-model="addForm.job_id"/>
    </el-form-item>
    <el-form-item label="执行策略">
      <el-tabs v-model="addForm.trigger" type="border-card" style="width: 100%">
        <el-tab-pane label="普通任务" name="date">
          <el-input/>
          <el-date-picker placeholder="执行时间"/>
        </el-tab-pane>
        <el-tab-pane label="定时任务" name="cron">
          <el-input v-model="addForm.cron_args.cron" placeholder="格式:分 时 日 月 周"/>
          <el-row>
            <el-col :span="12">
              <el-date-picker v-model="addForm.cron_args.start_date" style="width: 100%;" type="datetime"
                              value-format="YYYY-MM-DD HH:mm:ss" placeholder="开始时间"/>
            </el-col>
            <el-col :span="12">
              <el-date-picker v-model="addForm.cron_args.end_date" style="width: 100%;" type="datetime"
                              value-format="YYYY-MM-DD HH:mm:ss" placeholder="结束时间"/>
            </el-col>
          </el-row>
        </el-tab-pane>
      </el-tabs>
    </el-form-item>
    <el-form-item label="执行方式">
      <el-tabs type="border-card" style="width: 100%">
        <el-tab-pane label="单行命令">
          <el-input v-model="addForm.command" style="padding: 5px" placeholder="请输入执行命令"/>
        </el-tab-pane>
        <el-tab-pane label="脚本">在脚本页面创建脚本，然后这里选择对应脚本</el-tab-pane>
      </el-tabs>
    </el-form-item>
    <el-form-item>
      <el-button type="primary" @click="handleAdd">提交</el-button>
      <el-button>取消</el-button>
    </el-form-item>
  </el-form>
</template>

<script>
  export default {
    name: 'AddJob'
  }
</script>

<script setup>
  import {ref, reactive, onMounted} from 'vue'
  import {PostNewCronJob, PutCronJob} from '@/api/jobs'
  import {ElNotification} from 'element-plus'

  const props = defineProps(['job', 'visible'])
  const emit = defineEmits(['update:visible'])
  const addForm = reactive({
    job_id: null,
    trigger: 'cron',
    date_args: {
      run_date: null
    },
    cron_args: {
      cron: null,
      start_date: null,
      end_date: null,
    },
    command: null,
    type: '0'
  })

  if (props.job !== null) {
    Object.assign(addForm, props.job)
  }


  function handleAdd() {
    if (props.job === null) {
      PostNewCronJob(addForm).then(response => {
        ElNotification({
          title: 'success',
          message: '任务添加成功:' + response,
          type: 'success'
        })
      }).catch(error => {
        console.log(error)
      })
    } else {
      PutCronJob(addForm).then(response => {
        ElNotification({
          title: 'success',
          message: '任务修改成功:' + response,
          type: 'success'
        })
      }).catch(error => {
        console.log(error)
      })
    }

    emit('update:visible', false)
  }


</script>

<style scoped>
.date-range {
  padding: 10px;
  width: 100%;
}

</style>
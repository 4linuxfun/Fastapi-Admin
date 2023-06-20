<template>
  <div style="margin: 10px 10%;">
    <el-steps :space="200" :active="active" finish-status="success" simple>
      <el-step title="创建任务"/>
      <el-step title="选择执行对象"/>
      <el-step title="设置触发器"/>
    </el-steps>

    <el-form v-model="addForm" style="margin: 10px;">

      <!--任务信息-->
      <div v-show="active===0" style="margin-top: 20px;">
        <el-form-item label="任务名称">
          <el-input v-model="addForm.name"/>
        </el-form-item>
        <el-form-item label="执行方式">
          <el-tabs type="border-card" style="width: 100%">
            <el-tab-pane label="单行命令">
              <el-input v-model="addForm.command" style="padding: 5px" placeholder="请输入执行命令"/>
            </el-tab-pane>
            <el-tab-pane label="脚本">在脚本页面创建脚本，然后这里选择对应脚本</el-tab-pane>
          </el-tabs>
        </el-form-item>
      </div>

      <!--执行对象-->
      <div v-show="active === 1" style="margin-top: 20px;">
        <el-form-item label="执行对象">

        </el-form-item>
      </div>

      <!--执行策略页面-->
      <div v-show="active === 2" style="margin-top: 20px;">
        <el-row>
          <el-col :span="18" :offset="4">
            <el-tabs tab-position="left" v-model="addForm.trigger">
              <el-tab-pane label="定时任务" name="date">
                <el-form-item>
                  <span>执行时间</span>
                  <el-date-picker v-model="dateArgs" style="width: 100%;" type="datetime"
                                  value-format="YYYY-MM-DD HH:mm:ss" placeholder="请选择执行时间"/>
                  <span style="color:#99a9bf">不指定时间表示立即执行。</span>
                </el-form-item>

              </el-tab-pane>
              <el-tab-pane label="周期任务" name="cron">
                <el-form-item>
                  <span>执行规则</span>
                  <el-input v-model="cronArgs.cron" placeholder="格式:分 时 日 月 周"/>
                  <span>开始时间</span>
                  <el-date-picker v-model="cronArgs.start_date" style="width: 100%;" type="datetime"
                                  value-format="YYYY-MM-DD HH:mm:ss" placeholder="开始时间"/>
                  <span>结束时间</span>
                  <el-date-picker v-model="cronArgs.end_date" style="width: 100%;" type="datetime"
                                  value-format="YYYY-MM-DD HH:mm:ss" placeholder="结束时间"/>

                </el-form-item>
              </el-tab-pane>
            </el-tabs>
          </el-col>
        </el-row>
      </div>


      <el-form-item>
        <el-button v-if="active===2" type="primary" @click="handleAdd">提交</el-button>
        <el-button v-if="active !==2" type="primary" @click="active++">下一步</el-button>
        <el-button v-if="active !== 0" @click="active--">上一步</el-button>
      </el-form-item>
    </el-form>
  </div>

</template>

<script>
  export default {
    name: 'AddJob'
  }
</script>

<script setup>
  import {ref, reactive, onMounted, watch} from 'vue'
  import {PostNewCronJob, PutCronJob} from '@/api/jobs'
  import {ElNotification} from 'element-plus'

  const props = defineProps(['job', 'visible'])
  const emit = defineEmits(['update:visible'])

  const active = ref(0)
  const addForm = reactive({
    id: null,
    name: null,
    trigger: 'date',
    trigger_args: null,
    command: null,
    type: '0'
  })

  const intervalArgs = ref(null)
  const dateArgs = ref(null)
  const cronArgs = reactive({
    cron: null,
    start_date: null,
    end_date: null
  })

  if (props.job !== null) {
    Object.assign(addForm, props.job)
    if (props.job.trigger === 'cron') {
      Object.assign(cronArgs, props.job.trigger_args)
    } else {
      dateArgs.value = props.job.trigger_args
    }

  }


  function handleAdd() {
    if (addForm.trigger === 'interval') {
      addForm.trigger_args = intervalArgs.value
    } else if (addForm.trigger == 'date') {
      addForm.trigger_args = dateArgs.value
    } else {
      addForm.trigger_args = cronArgs
    }
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

  watch(() => addForm.trigger, (trigger) => {
    console.log(trigger)
  })

</script>

<style scoped>
.date-range {
  padding: 10px;
  width: 100%;
}

</style>
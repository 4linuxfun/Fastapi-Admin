<template>
  <el-dialog v-model="visible" width="50%" destroy-on-close>
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
              <el-tab-pane label="Module">
                <div style="padding: 5px">
                  <el-select placeholder="选择模块" v-model="addForm.ansible_args.module" >
                  <el-option v-for="module in moduleArray" :key="module.value" :label="module.value"
                             :value="module.value"/>
                </el-select>
                </div>

                <el-input v-model="addForm.ansible_args.module_args" style="padding:5px" placeholder="请输入命令参数"/>
              </el-tab-pane>
              <el-tab-pane label="Playbook">在脚本页面创建脚本，然后这里选择对应脚本</el-tab-pane>
            </el-tabs>
          </el-form-item>
        </div>

        <!--执行对象-->
        <div v-show="active === 1" style="margin-top: 20px;">
          <div style="margin: 0 20%;">
            <el-form-item label="执行对象">
              <el-select v-model="addForm.targets" multiple style="width: 100%">
                <el-option label="本机" value="6"/>
              </el-select>
              <el-button style="margin-top:10px;width: 100%;" @click="handleAddTargets">添加执行对象</el-button>
            </el-form-item>
          </div>

        </div>

        <!--执行策略页面-->
        <div v-show="active === 2" style="margin-top: 20px;">
          <el-row>
            <el-col :span="18" :offset="4">
              <el-tabs tab-position="left" v-model="addForm.trigger">
                <el-tab-pane label="定时任务" name="date">
                  <el-form-item>
                    <span>执行时间</span>
                    <el-date-picker v-model="addForm.trigger_args.run_date" style="width: 100%;" type="datetime"
                                    value-format="YYYY-MM-DD HH:mm:ss" placeholder="请选择执行时间"/>
                    <span style="color:#99a9bf">不指定时间表示立即执行。</span>
                  </el-form-item>

                </el-tab-pane>
                <el-tab-pane label="周期任务" name="cron">
                  <el-form-item>
                    <span>执行规则</span>
                    <el-input v-model="addForm.trigger_args.cron" placeholder="格式:分 时 日 月 周"/>
                    <span>开始时间</span>
                    <el-date-picker v-model="addForm.trigger_args.start_date" style="width: 100%;" type="datetime"
                                    value-format="YYYY-MM-DD HH:mm:ss" placeholder="开始时间"/>
                    <span>结束时间</span>
                    <el-date-picker v-model="addForm.trigger_args.end_date" style="width: 100%;" type="datetime"
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
    <add-targets ref="addTargetsRef"/>
  </el-dialog>

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
  import AddTargets from '@/views/jobs/JobManage/AddTargets.vue'

  const emit = defineEmits(['success'])

  const moduleArray = [
    {
      value: 'ping'
    },
    {
      value: 'shell'
    }
  ]

  const visible = ref(false)
  const active = ref(0)
  const addForm = reactive({})
  const addTargetsRef = ref(null)
  const initForm = {
    id: null,
    name: null,
    targets: null,
    trigger: 'date',
    trigger_args: {
      run_date: null,
      cron: null,
      start_date: null,
      end_date: null
    },
    ansible_args: {
      module: '',
      module_args: '',
      playbook: ''
    }
  }


  const hostList = [
    {
      value: 'localhost',
      label: '本机'
    },
    {
      value: '172.16.8.36',
      label: '生产服务器'
    }
  ]

  // if (props.job !== null) {
  //   Object.assign(addForm, props.job)
  //   if (props.job.trigger === 'cron') {
  //     Object.assign(cronArgs, props.job.trigger_args)
  //   } else {
  //     dateArgs.value = props.job.trigger_args
  //   }
  //
  // }


  async function handleAdd() {
    if (addForm.id === null) {
      try {
        let response = await PostNewCronJob(addForm)
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
        let response = await PutCronJob(addForm)
        ElNotification({
          title: 'success',
          message: '任务修改成功:',
          type: 'success'
        })
      } catch (error) {
        console.log(error)
      }
    }
    visible.value = false
    emit('success')
  }

  function handleAddTargets() {
    addTargetsRef.value.add()
  }

  function add() {
    active.value = 0
    Object.assign(addForm, JSON.parse(JSON.stringify(initForm)))
    visible.value = true
  }

  function edit(job) {
    console.log(job)
    active.value = 0
    Object.assign(addForm, JSON.parse(JSON.stringify(job)))
    visible.value = true
  }

  defineExpose({add, edit})

</script>

<style scoped>
.date-range {
  padding: 10px;
  width: 100%;
}

</style>
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
            <el-radio-group v-model="moduleTypeRadio">
              <el-radio label="module" value="module"/>
              <el-radio label="playbook" value="playbook"/>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="执行参数">
            <!--            module选择-->
            <template v-if="moduleTypeRadio==='module'">
              <el-input v-model="addForm.ansible_args.module" style="margin: 5px" placeholder="请输入模块名称">
                <template #prepend>模块名称:</template>
              </el-input>
              <el-input v-model="addForm.ansible_args.module_args" style="margin: 5px" placeholder="请输入命令参数">
                <template #prepend>模块参数:</template>
              </el-input>
            </template>
            <!--            playbook选择-->
            <template v-else-if="moduleTypeRadio ==='playbook'">
              <el-select-v2 v-model="addForm.ansible_args.playbook" :options="playbooks"
                            :props="{value:'id',label:'name'}"
                            filterable remote :remote-method="getPlaybooks" :loading="loading"
                            style="margin: 5px" placeholder="请选择playbook脚本"/>
            </template>

          </el-form-item>
        </div>

        <!--执行对象-->
        <div v-show="active === 1" style="margin-top: 20px;">
          <div style="margin: 0 20%;">
            <el-form-item label="执行对象:">
              <el-row v-for="(target,index) in targetHosts" style="width: 100%" :key="target.id">
                <el-col :span="22">
                  <el-input v-model="targetHosts[index].name" disabled/>
                </el-col>
                <el-col :span="1">
                  <el-button type="danger" circle @click="targetHosts.splice(index,1)">
                    <el-icon>
                      <Minus/>
                    </el-icon>
                  </el-button>
                </el-col>
              </el-row>

            </el-form-item>
            <el-form-item>
              <el-button style="width: 100%;" @click="handleAddTargets">添加执行对象</el-button>
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


        <el-form-item style="margin-top: 10px">
          <el-button v-if="active===2" type="primary" @click="handleAdd">提交</el-button>
          <el-button v-if="active !==2" type="primary" @click="handleNextStep">下一步</el-button>
          <el-button v-if="active !== 0" @click="active--">上一步</el-button>
        </el-form-item>
      </el-form>
    </div>
    <add-targets ref="addTargetsRef" @success="updateTargets"/>
  </el-dialog>

</template>

<script>
  export default {
    name: 'AddJob'
  }
</script>

<script setup>
  import {ref, reactive, watch} from 'vue'
  import {PostNewCronJob, PutCronJob} from '@/api/jobs'
  import {ElNotification} from 'element-plus'
  import AddTargets from '@/views/jobs/JobManage/AddTargetsDialog.vue'
  import {Minus} from '@element-plus/icons-vue'
  import {GetHostsByIds} from '@/api/host.js'
  import {GetPlaybooksByQuery} from '@/api/playbook.js'

  const emit = defineEmits(['success'])
  const visible = ref(false)
  const active = ref(0)
  const addForm = reactive({})
  const addTargetsRef = ref(null)
  const targetHosts = ref([])
  const moduleTypeRadio = ref('module')
  const playbooks = ref([])
  const loading = ref(false)
  const value = ref('')

  // form表单的初始化值
  const initForm = {
    id: null,
    name: null,
    targets: [],
    trigger: 'date',
    trigger_args: {
      run_date: null,
      cron: null,
      start_date: null,
      end_date: null
    },
    ansible_args: {
      module: null,
      module_args: '',
      playbook: null
    }
  }

  function handleNextStep() {
    console.log(active.value)
    if (active.value === 0) {
      //  参数选择后，需要清空没选择的,module一定要为null，ansible-runner是判定module为None才会选择为playbook执行
      if (moduleTypeRadio.value === 'module') {
        addForm.ansible_args.playbook = null
      } else if (moduleTypeRadio.value === 'playbook') {
        addForm.ansible_args.module = null
        addForm.ansible_args.module_args = null
      }
    }
    console.log(addForm)
    active.value++
  }

  /**
   * 获取playbook列表
   * @param query
   */
  async function getPlaybooks(query) {
    if (query !== '') {
      console.log('start to search', query)
      loading.value = true
      playbooks.value = await GetPlaybooksByQuery(query)
    } else {
      playbooks.value = []
    }
    loading.value = false
  }

  /**
   * 确认按钮，提交任务
   * @return {Promise<void>}
   */
  async function handleAdd() {
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
    visible.value = false
    emit('success')
  }

  /**
   * addTargetsDialog触发success事件，表示更新主机列表
   * @param selectHosts
   */
  function updateTargets(selectHosts) {
    console.log(selectHosts)
    targetHosts.value = JSON.parse(JSON.stringify(selectHosts))
  }

  /**
   * 添加执行对象，弹出addTargetsDialog对话框
   * @return {Promise<void>}
   */
  async function handleAddTargets() {
    console.log(targetHosts.value)
    await addTargetsRef.value.add(targetHosts.value)
  }

  /**
   * 监听targetHosts的变化，更新addForm.targets
   */
  watch(targetHosts, () => {
    addForm.targets = targetHosts.value.map(item => item.id)
  }, {deep: true})

  /**
   * 添加任务
   */
  function add() {
    active.value = 0
    Object.assign(addForm, JSON.parse(JSON.stringify(initForm)))
    targetHosts.value = []
    moduleTypeRadio.value = 'module'
    visible.value = true
  }

  /**
   * 编辑任务
   * @param job
   * @return {Promise<void>}
   */
  async function edit(job) {
    console.log(job)
    active.value = 0
    Object.assign(addForm, JSON.parse(JSON.stringify(job)))
    console.log(addForm.targets)
    const paramsString = addForm.targets.map(item => `ids=${item}`).join('&')
    targetHosts.value = await GetHostsByIds(paramsString)
    console.log(targetHosts.value)
    playbooks.value = await GetPlaybooksByQuery(null)
    if (addForm.ansible_args.module !== null) {
      moduleTypeRadio.value = 'module'
    } else {
      moduleTypeRadio.value = 'playbook'
    }
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
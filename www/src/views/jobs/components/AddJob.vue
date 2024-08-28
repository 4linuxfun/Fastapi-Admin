<!--添加任务表单-->
<template>
  <el-form v-model="addForm" style="margin-top: 10px">
    <el-form-item label="任务名称" v-if="cronMode">
      <el-input v-model="addForm.name"/>
    </el-form-item>

    <el-form-item label="执行方式">
      <el-radio-group v-model="moduleTypeRadio">
        <el-radio-button label="module" value="module"/>
        <el-radio-button label="playbook" value="playbook"/>
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

    <!--    任务执行时间设定-->
    <el-tabs v-if="cronMode" tab-position="left" v-model="addForm.trigger">
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
    <!--    添加执行主机-->
    <el-form-item label="执行主机">
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
      <el-button style="width: 100%;" @click="handleAddTargets">添加执行主机</el-button>
    </el-form-item>
  </el-form>
  <el-row justify="center">
    <el-button type="danger" @click="emit('cancel')">取消</el-button>
    <el-button type="primary" @click="handleSubmit">确定</el-button>
  </el-row>
  <add-targets-dialog ref="addTargetsRef" @success="updateTargets"/>
</template>

<script setup>
  import {ref, reactive, watch, onMounted} from 'vue'
  import {GetHostsByIds} from '@/api/host.js'
  import {GetPlaybooksByQuery} from '@/api/playbook.js'
  import {Minus} from '@element-plus/icons-vue'
  import AddTargetsDialog from './AddTargetsDialog.vue'

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

  // cron为true，则为定时任务，会显示对应的选择框
  const props = defineProps({
    data: {type: Object},
    cron: {type: Boolean, default: false}
  })
  // submit确认按钮，cancel取消按钮
  const emit = defineEmits(['submit', 'cancel'])
  const addTargetsRef = ref(null)
  const addForm = ref(initForm)

  const moduleTypeRadio = ref('module')
  const playbooks = ref([])
  const loading = ref(false)
  const targetHosts = ref([])
  const cronMode = ref(props.cron)

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

  /*
  * 确认按钮，需要对表单数据进行操作
   */
  function handleSubmit() {
    emit('submit', addForm.value)
  }

  /**
   * 监听targetHosts的变化，更新addForm.targets
   */
  watch(targetHosts, () => {
    addForm.value.targets = targetHosts.value.map(item => item.id)
  }, {deep: true})

  /**
   * 添加任务
   */
  function add() {
    addForm.value = initForm
    targetHosts.value = []
    moduleTypeRadio.value = 'module'
  }

  /**
   * 编辑任务
   * @return {Promise<void>}
   */
  async function edit() {
    // console.log(job)
    // Object.assign(addForm, JSON.parse(JSON.stringify(job)))
    addForm.value = JSON.parse(JSON.stringify(props.data))
    console.log(addForm.value.targets)
    const paramsString = addForm.value.targets.map(item => `ids=${item}`).join('&')
    targetHosts.value = await GetHostsByIds(paramsString)
    console.log(targetHosts.value)
    playbooks.value = await GetPlaybooksByQuery(null)
    if (addForm.value.ansible_args.module !== null) {
      moduleTypeRadio.value = 'module'
    } else {
      moduleTypeRadio.value = 'playbook'
    }
  }

  onMounted(async () => {
    console.log('mount add job')
    if (props.data === null) {
      add()
    } else {
      console.log(props.data)
      await edit()
    }
  })

</script>
<style scoped>
:deep(.el-tabs__item) {
  padding-left: 0;
}
</style>
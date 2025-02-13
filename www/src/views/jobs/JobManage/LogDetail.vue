<!--
  用户展示任务执行日志的单个详情
-->
<template>
  <el-dialog v-model="visible" title="任务日志" destroy-on-close>
    <div>
      <el-descriptions border :column="2">
        <el-descriptions-item label="开始时间">{{ taskLogInfo.start_time }}</el-descriptions-item>
        <el-descriptions-item label="结束时间">{{ taskLogInfo.end_time }}</el-descriptions-item>
        <el-descriptions-item label="成功主机">
          <el-descriptions border :column="2">
            <template v-if="taskStats !== null">
              <template v-for="(num,host, index) in taskStats.ok" :key="index">
                <el-descriptions-item label="主机">{{ host }}</el-descriptions-item>
                <el-descriptions-item label="结果">{{ num }}</el-descriptions-item>
              </template>
            </template>
          </el-descriptions>
        </el-descriptions-item>
        <el-descriptions-item label="失败主机">
          <el-descriptions border :column="2">
            <template v-if="taskStats !== null">
              <template v-for="(num,host, index) in taskStats.failures" :key="index">
                <el-descriptions-item label="主机">{{ host }}</el-descriptions-item>
                <el-descriptions-item label="结果">{{ num }}</el-descriptions-item>
              </template>
            </template>

          </el-descriptions>
        </el-descriptions-item>
        <el-descriptions-item label="执行日志" :span="1">
          <div ref="terminalRef" style="width: 100%;height: 100%"/>
        </el-descriptions-item>
      </el-descriptions>
    </div>

  </el-dialog>

</template>

<script setup>
  import {reactive, ref, computed, onMounted, nextTick} from 'vue'
  import useTerm from '@/composables/useTerm.js'

  const visible = ref(false)
  const taskLogInfo = reactive({})
  const taskLogs = ref('')
  const taskStats = computed(() => {
    return JSON.parse(taskLogInfo.stats)
  })
  console.log('init log detail')
  const terminalRef = ref(null)
  const {term, initTerm} = useTerm(terminalRef)


  async function show(log) {
    visible.value = true
    Object.assign(taskLogInfo, JSON.parse(JSON.stringify(log)))
    console.log(taskLogInfo)
    await nextTick(async () => {
      await initTerm()
    })

    let data = JSON.parse(taskLogInfo.log)
    data.forEach(item => {
      // taskLogs.value += item[1].msg
      term.value.write(item[1].msg + '\n')
    })
  }

  onMounted(() => {
    console.log('mountd log detail')

  })

  defineExpose({
    show
  })
</script>

<style scoped>

</style>
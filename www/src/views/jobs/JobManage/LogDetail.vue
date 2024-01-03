<template>
  <el-row>
    <el-col :span="8">
      <span style="font-size: xx-large">执行成功</span>
      <p>
        <span style="font-size:xx-large;color: #519118">{{ status.success }}</span>
      </p>
    </el-col>
    <el-col :span="8">
      <span style="font-size: xx-large">执行失败</span>
      <p>
        <span style="font-size: xx-large;color: #db4f5a;">{{ status.failure }}</span>
      </p>
    </el-col>
    <el-col :span="8">
      <span style="font-size: xx-large">平均耗时(秒)</span>
      <p>
        <span style="font-size: xx-large;">{{status.duration}}</span>
      </p>
    </el-col>
  </el-row>
  <el-tabs tab-position="left" style="margin: 10px 10% 0;">
    <template v-for="(value,key) in props.log">
      <el-tab-pane :label="key">
      <el-row style="margin-top: 5px;">运行耗时：{{value['duration']}}</el-row>
      <el-row style="margin-top: 5px;">返回状态：{{value['status']}}</el-row>
      <el-row style="margin-top: 5px;">执行日志：{{hostLogs[key]}}</el-row>
    </el-tab-pane>
    </template>

  </el-tabs>
</template>

<script setup>
  import {reactive, onMounted} from 'vue'

  const props = defineProps(['log'])
  const status = reactive({
    success: 0,
    failure: 0,
    duration: 0
  })

  const hostLogs = reactive({})

  function formatLog(log){
    let logDetail = ''
    log.forEach((value) => {
      let [timestamp, data] = value
      let date = new Date(Number(timestamp.split('-')[0]))
      //包含type属性，说明需要做判断，没有type属性的一律为普通输出信息
      if (data.hasOwnProperty('type')) {
        if (data.type === 'table') {
          taskLog['result'].push(JSON.parse(data.msg))
        } else if (data.type === 'error') {
          if (logAttach) {
            taskLog['log'] += '\x1B[1;3;31m' + data.msg + '\x1B[0m\r\n'
          } else {
            taskLog['log'] = '\x1B[1;3;31m' + data.msg + '\x1B[0m\r\n'
          }
          taskLog['fail'] += 1
        } else if (data.type === 'success') {
          if (logAttach) {
            taskLog['log'] += data.msg + '\r\n'
          } else {
            taskLog['log'] = data.msg + '\r\n'
          }
          taskLog['success'] += 1
        }
      } else {
        if (logAttach) {
          taskLog['log'] += data.msg + '\r\n'
        } else {
          taskLog['log'] = data.msg + '\r\n'
        }

      }
    })
  }

  onMounted(() => {
    console.log(props.log)
    let totalTime = 0
    for (let key in props.log) {
      totalTime+= props.log[key]['duration']
      if (props.log[key].status === 0) {
        status.success += 1
      } else {
        status.failure += 1
      }

      hostLogs[key] = props.log[key]['log']
    }
    status.duration = totalTime/(Object.keys(props.log)).length
  })


</script>

<style scoped>

</style>
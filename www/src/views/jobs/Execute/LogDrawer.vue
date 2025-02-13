<template>
  <el-drawer v-model="visible" title="执行任务日志" size="70%" destroy-on-close>
    <div ref="terminalRef" style="width: 100%;height: 100%"/>
  </el-drawer>
</template>

<script setup>
  import {ref, nextTick, onBeforeUnmount} from 'vue'
  import useTerm from '@/composables/useTerm.js'
  import {AttachAddon} from 'xterm-addon-attach'

  const visible = ref(false)
  const terminalRef = ref(null)
  const {term, initTerm} = useTerm(terminalRef)
  const ws = ref(null)


  async function show(taskId) {
    console.log('show log drawer')
    visible.value = true
    await nextTick(async () => {
      await initTerm()
    })
    console.log('init ok')
    term.value.write('Welcome to use Ansible!\r\n')
    term.value.write('正在连接中，请等待。。。。\r\n')
    // 立即执行，后台可能还没有执行，需要等待几秒进行连接
    await new Promise((resolve) => setTimeout(resolve, 3000))
    ws.value = new WebSocket(import.meta.env.VITE_APP_WS + '/api/jobs/logs/ws/' + taskId)
    term.value.write('连接成功，等待接收执行日志！\r\n')
    const attachAddon = new AttachAddon(ws.value)
    term.value.loadAddon(attachAddon)
  }

  onBeforeUnmount(() => {
    if (ws.value && ws.value.close) {
      ws.value.close()
    }
  })

  defineExpose({show})
</script>


<style scoped>

</style>
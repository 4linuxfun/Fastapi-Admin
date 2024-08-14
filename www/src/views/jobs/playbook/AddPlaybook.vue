<!--新增和编辑playbook页面-->
<template>
  <el-dialog v-model="visible" :title="title" destroy-on-close>
    <el-form>
      <el-form-item label="Playbook名称">
        <el-input v-model="playBook.name" placeholder="请输入playbook名称"/>
      </el-form-item>
      <el-form-item label="Playbook内容">
      </el-form-item>
      <v-ace-editor v-model:value="playBook.playbook" lang="yaml" theme="tomorrow"
                    style="height: 300px;margin-bottom: 10px"/>
      <el-form-item label="Playbook描述">
        <el-input v-model="playBook.desc" placeholder="请增加playbook的附加描述信息" type="textarea" :rows="5"/>
      </el-form-item>

    </el-form>
    <el-row justify="center">
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="save">保存</el-button>
    </el-row>
  </el-dialog>
</template>

<script setup>
  import {ref, reactive} from 'vue'
  import {VAceEditor} from 'vue3-ace-editor'
  import ace from 'ace-builds'
  import modeYamlUrl from 'ace-builds/src-noconflict/mode-yaml?url'
  import themeTomorrow from 'ace-builds/src-noconflict/theme-tomorrow?url'
  import snippetsYamlUrl from 'ace-builds/src-noconflict/snippets/yaml?url'
  import {PostNewPlaybook, PutPlaybook} from '@/api/playbook.js'

  ace.config.setModuleUrl('ace/mode/yaml', modeYamlUrl)
  ace.config.setModuleUrl('ace/theme/tomorrow', themeTomorrow)
  ace.config.setModuleUrl('ace/snippets/yaml', snippetsYamlUrl)

  const emit = defineEmits(['close'])
  const visible = ref(false)
  const title = ref('')
  const playBook = reactive({})
  const initPlayBook = {
    id: null,
    name: null,
    playbook: '',
    desc: null
  }
  let RequestAPI = null

  async function save() {
    try {
      await RequestAPI(playBook)
    } catch (err) {
      console.log('error submit', err)
    }
    visible.value = false
    emit('close')
  }


  function add() {
    title.value = '新增Playbook'
    Object.assign(playBook, JSON.parse(JSON.stringify(initPlayBook)))
    RequestAPI = PostNewPlaybook
    visible.value = true
  }

  function edit(data) {
    title.value = '编辑Playbook'
    Object.assign(playBook, JSON.parse(JSON.stringify(data)))
    RequestAPI = PutPlaybook
    visible.value = true
  }

  defineExpose({
    add,
    edit
  })
</script>
<style scoped>

</style>
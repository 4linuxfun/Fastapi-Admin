<template>
  <el-dialog v-model="visible" :title="title" width="700">
    <el-form>
      <el-form-item label="主机分组">
        <el-tree-select v-model="hostForm.groups" :data="allGroups" :props="{label:'name'}" value-key="id" multiple
                        check-strictly
                        :render-after-expand="false"
                        check-on-click-node>
          <template #label="{label,value}">
            <span>{{ getHierarchyLabel(allGroups, value, {label: 'name'}) }}</span>
          </template>
        </el-tree-select>
      </el-form-item>
      <el-form-item label="主机名称" prop="name">
        <el-input v-model="hostForm.name" placeholder="请输入主机名称"/>
      </el-form-item>
      <el-form-item label="连接地址">
        <el-row>
          <el-col :span="6">
            <el-input v-model="hostForm.ansible_user" placeholder="用户名">
              <template #prepend>ssh</template>
            </el-input>
          </el-col>
          <el-col :span="12">
            <el-input v-model="hostForm.ansible_host" placeholder="主机名/IP">
              <template #prepend>@</template>
            </el-input>
          </el-col>
          <el-col :span="6">
            <el-input v-model="hostForm.ansible_port" placeholder="端口">
              <template #prepend>-p</template>
            </el-input>
          </el-col>
        </el-row>
      </el-form-item>
      <el-form-item label="独立密钥">
        <el-input type="textarea" :rows="5" v-model="hostForm.ansible_ssh_private_key"
                  placeholder="默认使用全局密钥，如果上传了独立密钥（私钥）则优先使用该密钥。"/>
      </el-form-item>
      <el-form-item label="备注信息" prop="desc">
        <el-input type="textarea" :rows="2" v-model="hostForm.desc" placeholder="请输入主机备注信息"/>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="visible=false">取消</el-button>
      <el-button type="primary" @click="handleAdd">保存</el-button>
      <el-button type="primary" @click="handleCheck">验证</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
  import {ref, reactive} from 'vue'
  import {GetAllGroup, GetHostById, PostNewHost, PutHost, PingHost} from '@/api/host.js'
  import {ElNotification} from 'element-plus'
  import {getHierarchyLabel} from '@/utils/common.js'

  const initForm = {
    id: null,
    name: null,
    groups: null,
    ansible_host: null,
    ansible_port: 22,
    ansible_user: 'root',
    ansible_password: null,
    ansible_ssh_private_key: null,
    desc: null
  }

  const emit = defineEmits(['close'])
  const visible = ref(false)
  const title = ref('')
  const hostForm = reactive({...initForm})
  const allGroups = ref([])
  const isEdit = ref(false)


  async function handleAdd() {
    console.log(hostForm)
    if (isEdit.value) {
      try {
        await PutHost(hostForm)
        ElNotification.success('更新成功')
      } catch (err) {
        ElNotification.error('更新失败:' + err)
      }
    } else {
      try {
        await PostNewHost(hostForm)
        ElNotification.success('添加成功')
      } catch (err) {
        ElNotification.error('添加失败:' + err)
      }
    }
    visible.value = false
    emit('close')
  }

  function handleCheck() {
    // 先添加主机，后检查主机可用性
    // 新建主机流程：添加主机+验证
    // 编辑主机：更新主机+验证
    PingHost(hostForm.id)
    console.log('主机验证')
  }

  async function add() {
    isEdit.value = false
    try {
      allGroups.value = await GetAllGroup()
    } catch (err) {
      console.log('获取组失败。。。')
      return false
    }
    title.value = '新建主机'
    Object.assign(hostForm, initForm)
    visible.value = true
  }

  async function edit(hostId) {
    isEdit.value = true
    try {
      allGroups.value = await GetAllGroup()
      let host = await GetHostById(hostId)
      Object.assign(hostForm, host)
    } catch (err) {
      console.log('获取组失败。。。')
      return false
    }
    title.value = '编辑主机'
    console.log(hostForm)
    visible.value = true
  }

  defineExpose({add, edit})
</script>

<style scoped>

</style>
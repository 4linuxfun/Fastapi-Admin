<!--
  新增、编辑分组对话框
-->
<template>
  <el-dialog v-model="visible" width="500px" :title="title" destroy-on-close>
    <el-form ref="addRootFormRef" :model="addRootForm" label-width="100px">
      <el-form-item label="父级：">
        <el-tree-select v-model="addRootForm.parent_id" :data="allGroups" :props="{label:'name'}" value-key="id"
                        check-strictly
                        :render-after-expand="false"
                        check-on-click-node
                        @change="handleChangeAncestors">
          <template #label="{label,value}">
            <span>{{ getHierarchyLabel(allGroups, value, {label: 'name'}) }}</span>
          </template>
        </el-tree-select>
      </el-form-item>
      <el-form-item label="分组名：" prop="name" :rules="[{required:true,message:'请输入分组名'}]">
        <el-input v-model="addRootForm.name"/>
      </el-form-item>
    </el-form>
    <el-row justify="end">
      <el-button type="primary" @click="handleAddRoot">提交</el-button>
      <el-button type="danger" @click="visible=false">取消</el-button>
    </el-row>
  </el-dialog>
</template>

<script setup>
  import {reactive, ref} from 'vue'
  import {PostNewGroup, PutGroup, GetAllGroup} from '@/api/host.js'
  import {findNodeById, getHierarchyLabel} from '@/utils/common.js'

  const emit = defineEmits(['close'])
  const addRootFormRef = ref(null)
  const visible = ref(false)
  const title = ref('')
  const addRootForm = reactive({})
  const allGroups = ref([])
  let RequestAPI = ref(null)

  const initRootForm = {id: null, name: null, parent_id: null, ancestors: null}


  /**
   * 下拉框选择父组件后，对应的ancestors属性值也需要修改
   * @param id
   */
  function handleChangeAncestors(id) {
    let selectNode = findNodeById(allGroups.value, id)
    console.log(selectNode)
    if (selectNode.ancestors === null || selectNode.ancestors === undefined || selectNode.ancestors === '') {
      // 为空，则为根节点
      addRootForm.ancestors = selectNode.id.toString()
    } else {
      // 父节点存在ancestors，继承拼接
      addRootForm.ancestors = selectNode.ancestors + ',' + selectNode.id.toString()
    }
    console.log(addRootForm)
  }

  /**
   * 添加根分组的函数
   */
  async function handleAddRoot() {
    console.log('添加根分组')
    // treeData.value.push({label: '', children: []})
    try {
      await addRootFormRef.value.validate()
      console.log('submit')
      await RequestAPI(addRootForm)
    } catch (err) {
      console.log('error submit', err)
    }
    visible.value = false
    emit('close')
  }


  async function add() {
    console.log('start to get all groups')
    try {
      allGroups.value = await GetAllGroup()
    } catch (err) {
      console.log('获取组失败。。。')
      return false
    }
    Object.assign(addRootForm, initRootForm)
    console.log('start to visible')
    console.log(allGroups.value)
    RequestAPI = PostNewGroup
    title.value = '新增分组'
    visible.value = true
  }

  async function edit(data) {
    try {
      allGroups.value = await GetAllGroup()
    } catch (err) {
      console.log('获取组失败。。。')
      return false
    }
    Object.assign(addRootForm, data)
    RequestAPI = PutGroup
    title.value = '编辑分组'
    visible.value = true
  }

  defineExpose({add, edit})
</script>


<style scoped>

</style>
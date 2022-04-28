<template>
  <el-dialog :model-value="visible" title="菜单编辑页面" width="30%" @close="$emit('update:visible', false)"
             destroy-on-close>
    <el-form :model="selectData" label-width="80px">
      <el-form-item label="菜单ID" v-if="selectData.id">{{ selectData.id }}</el-form-item>
      <el-form-item label="父菜单">{{ selectData.parent_id }}</el-form-item>
      <el-form-item label="名称">
        <el-input v-model="selectData.name"></el-input>
      </el-form-item>
      <el-form-item label="路径">
        <el-input v-model="selectData.path"></el-input>
      </el-form-item>
      <el-form-item v-if="selectData.type === 'page'" label="组件">
        <!-- <el-input v-if="selectData.parent_id == null" v-model="selectData.component" disabled></el-input> -->
        <el-input v-model="selectData.component"></el-input>
      </el-form-item>
      <el-form-item v-else-if="selectData.type === 'button'" label="URL地址">
        <el-input v-model="selectData.url"></el-input>
      </el-form-item>
      <el-form-item label="关联API接口权限">
        <el-select v-model="selectApis" filterable multiple placeholder="选择接口" style="width:100%">
          <el-option-group v-for="group in totalApiLists" :key="group.label" :label="group.label">
            <el-option v-for="item in group.options" :key="item.id" :label="item.summary" :value="item.id"></el-option>
          </el-option-group>
        </el-select>
      </el-form-item>
      <el-form-item label="状态">
        <el-radio-group v-model="selectData.enable">
          <el-radio :label="0" size="medium">禁用</el-radio>
          <el-radio :label="1" size="medium">启用</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item>
        <el-button @click="$emit('update:visible', false)">取消</el-button>
        <!-- 更新和添加按钮触发的事件都是一样的，只是提交数据时id字段为空，此需要服务端通过此字段去判断添加还是更新 -->
        <el-button type="primary" @click="handleUpdate" v-if="selectData.id">更新</el-button>
        <el-button type="primary" @click="handleUpdate" v-else>添加</el-button>
      </el-form-item>
    </el-form>
  </el-dialog>

  <!-- 编辑按钮对话框内容 -->
</template>

<script>
  import {
    PostNewMenu,
    PutMenu,
    GetMenuTreeApis
  } from '@/api/menus'
  import {
    ref,
    reactive
  } from 'vue'

  export default {

    props: ['data', 'visible'],
    emits: ['update:visible'],
    setup(props, {
      emit
    }) {
      const selectData = reactive(props.data)
      const loading = ref(false)
      const totalApiLists = ref([])
      const selectApis = ref([])
      GetMenuTreeApis().then(response => {
        totalApiLists.value = response
      })

      for (const api of selectData.apis){
        console.log(api)
        selectApis.value.push(api.id)
      }

      const handleUpdate = () => {
        console.log(selectData)
        if (selectData.id === null) {
          console.log('新建菜单')
          PostNewMenu(selectData)
        } else {
          selectData.apis = selectApis.value
          PutMenu(selectData)
        }
        emit('update:visible', false)
      }

      return {
        selectApis,
        totalApiLists,
        selectData,
        loading,
        handleUpdate,
      }
    },
  }
</script>

<style>
</style>

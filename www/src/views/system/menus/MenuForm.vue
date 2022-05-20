<template>
  <el-form-item label="菜单名称" prop="name" :rules="[{required:true,message:'请填写菜单名称'}]">
    <el-input v-model="selectData.name"></el-input>
  </el-form-item>
  <el-form-item v-if="selectData.type ==='subPage'" label="父菜单">
    <el-cascader v-model="selectData.parent_id" :options="menuData" :props="{checkStrictly:true,value:'id'}"
                 placeholder="请选择父菜单">
    </el-cascader>
  </el-form-item>
  <el-form-item label="菜单路径" prop="path" :rules="[{required:true,message:'请填写菜单路径'}]">
    <el-input v-model="selectData.path"></el-input>
  </el-form-item>
  <el-form-item v-if="selectData.type === 'page'" label="前端组件" prop="component"
                :rules="[{required:true,message:'一级菜单填写Layout'}]">
    <!-- <el-input v-if="selectData.parent_id == null" v-model="selectData.component" disabled></el-input> -->
    <el-input v-model="selectData.component"></el-input>
  </el-form-item>
  <el-form-item v-else-if="selectData.type === 'btn'" label="URL地址">
    <el-input v-model="selectData.url"></el-input>
  </el-form-item>
  <el-form-item label="关联API接口">
    <el-select v-model="selectApis" filterable multiple placeholder="选择接口" style="width:100%">
      <el-option-group v-for="group in totalApiLists" :key="group.label" :label="group.label">
        <el-option v-for="item in group.options" :key="item.id" :label="item.summary" :value="item.id"></el-option>
      </el-option-group>
    </el-select>
  </el-form-item>
  <el-form-item label="状态">
    <el-radio-group v-model="selectData.enable">
      <el-radio :label="0">禁用</el-radio>
      <el-radio :label="1">启用</el-radio>
    </el-radio-group>
  </el-form-item>
</template>

<script>
  import {toRefs, reactive, ref, watch, inject} from 'vue'

  export default {
    name: 'MenuForm',
    props: ['form', 'totalApiLists'],
    emits: ['update:form'],
    setup(props, {emit}) {
      const {form} = toRefs(props)
      const selectData = reactive(form.value)
      const loading = ref(false)
      const selectApis = ref([])

      const menuData = inject('menuData')
      if (selectData.id !== null) {
        for (const api of selectData.apis) {
          console.log(api)
          selectApis.value.push(api.id)
        }
      }

      watch(selectData, (newData) => {
        console.log('watch selectData change:' + selectData)
        emit('update:form', selectData)
      })

      watch(selectApis, (newValue) => {
        console.log('selectApi watch')
        selectData.apis = selectApis.value
      })

      return {
        selectData,
        menuData,
        selectApis,
        loading,
      }
    },
  }
</script>

<style scoped>

</style>
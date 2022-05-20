<template>
  <el-form-item label="按钮:" prop="name" :rules="[{required:true,message:'请填写按钮名称'}]">
    <el-input v-model="selectData.name"></el-input>
  </el-form-item>
  <el-form-item label="上级菜单" :rules="[{required:true,message:'请选择上级菜单'}]">
    <el-input v-model="selectData.parent_id"></el-input>
  </el-form-item>
  <el-form-item label="授权标识" prop="path" :rules="[{required:true,message:'请填写按钮授权标识'}]">
    <el-input v-model="selectData.path"></el-input>
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
    name: 'ButtonForm',
    props: ['form', 'totalApiLists'],
    emits: ['update:form'],
    setup(props, {emit}) {
      const {form} = toRefs(props)
      const selectData = reactive(form.value)
      const loading = ref(false)
      const selectApis = ref([])

      const menuData = inject('menuData')
      if(selectData.id !== null){
        for (const api of selectData.apis) {
          console.log(api)
          selectApis.value.push(api.id)
        }
      }


      watch(selectData, (newData) => {
        console.log('watch selectData change:' + selectData)
        emit('update:form', selectData)
      })

      watch(selectApis,(newValue)=>{
        console.log('selectApi watch')
        selectData.apis = selectApis.value
      })

      return {
        selectData,
        menuData,
        loading,
        selectApis
      }
    },
  }
</script>

<style scoped>

</style>
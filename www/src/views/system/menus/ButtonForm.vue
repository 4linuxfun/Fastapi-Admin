<template>
  <el-form-item label="按钮:" prop="name" :rules="[{required:true,message:'请填写按钮名称'}]">
    <el-input v-model="selectData.name"></el-input>
  </el-form-item>
  <el-form-item label="上级菜单" prop="parent_id" :rules="[{required:true,message:'请选择上级菜单'}]">
    <el-cascader v-model="selectData.parent_id" :options="cascaderMenu"
                 :props="{checkStrictly:true,value:'id',label:'name',emitPath:false}"
                 placeholder="请选择父菜单" style="width:100%">
    </el-cascader>
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
      <el-radio :label=false>禁用</el-radio>
      <el-radio :label=true>启用</el-radio>
    </el-radio-group>
  </el-form-item>
</template>

<script setup>
  import {toRefs, reactive, ref, inject} from 'vue'
  import useMenu from '@/composables/useMenu'

  const props = defineProps(['form', 'totalApiLists'])
  const emit = defineEmits(['update:form'])

  const {form} = toRefs(props)
  const loading = ref(false)

  const menuData = inject('menuData')
  const {selectData, selectApis, cascaderMenu} = useMenu(form.value, menuData.value, emit)
</script>

<style scoped>

</style>
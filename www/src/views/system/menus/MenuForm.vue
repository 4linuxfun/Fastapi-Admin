<template>
  <el-form-item label="菜单名称" prop="name" :rules="[{required:true,message:'请填写菜单名称'}]">
    <el-input v-model="selectData.name"></el-input>
  </el-form-item>
  <el-form-item v-if="selectData.type ==='subPage'" label="父菜单">
    <el-cascader v-model="selectData.parent_id" :options="cascaderMenu"
                 :props="{checkStrictly:true,value:'id',label:'name',emitPath:false}"
                 placeholder="请选择父菜单" style="width:100%">
    </el-cascader>
  </el-form-item>
  <el-form-item label="菜单路径" prop="path" :rules="[{required:true,message:'请填写菜单路径'}]">
    <el-input v-model="selectData.path"></el-input>
  </el-form-item>
  <el-form-item v-if="selectData.type !== 'btn'" label="前端组件" prop="component"
                :rules="[{required:true,message:'一级菜单填写Layout'}]">
    <!-- <el-input v-if="selectData.parent_id == null" v-model="selectData.component" disabled></el-input> -->
    <el-input v-model="selectData.component"></el-input>
  </el-form-item>
  <el-form-item v-else label="URL地址">
    <el-input v-model="selectData.url"></el-input>
  </el-form-item>
  <el-form-item label="状态">
    <el-radio-group v-model="selectData.enable">
      <el-radio :label=false>禁用</el-radio>
      <el-radio :label=true>启用</el-radio>
    </el-radio-group>
  </el-form-item>
</template>

<script>
  import {toRefs, reactive, ref, watch, inject, computed} from 'vue'
  import useMenu from '@/composables/useMenu'

  export default {
    name: 'MenuForm',
    props: ['form', 'totalApiLists'],
    emits: ['update:form'],
    setup(props, {emit}) {
      const {form} = toRefs(props)
      const loading = ref(false)

      const menuData = inject('menuData')

      const {selectData, cascaderMenu} = useMenu(form.value, menuData.value, emit)


      return {
        selectData,
        menuData,
        cascaderMenu,
        loading,
      }
    },
  }
</script>

<style scoped>

</style>
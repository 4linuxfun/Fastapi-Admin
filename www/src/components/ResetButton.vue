<template>
  <el-button type="primary" :icon="Refresh" @click="handleReset">重置</el-button>
</template>

<script setup>
  import {Refresh} from '@element-plus/icons-vue'
  import {toRefs} from 'vue'

  const props = defineProps(['searchRef'])
  const emit = defineEmits(['handleSearch'])
  const {searchRef} = toRefs(props)

  function handleReset() {
    searchRef.value.resetFields()
    emit('handleSearch')
  }
</script>

<style scoped>

</style>
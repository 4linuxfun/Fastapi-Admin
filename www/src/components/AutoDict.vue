<template>
  <!--数据字典自动带出组件。通过提供的URL获取信息，并根据需要选择相应的组件进行展示-->
  <template v-if="type==='select'">
    <el-select  v-model="value" @change="handleUpdate">
      <el-option v-for="item in itemArray" :key="item.value" :label="item.label" :value="item.value"/>
    </el-select>
  </template>

  <template v-else-if="type === 'switch'">
    <el-switch v-model="value" @change="handleUpdate"
               style="--el-switch-on-color: #13ce66; --el-switch-off-color: #ff4949"/>
  </template>
</template>

<script setup>
  import {onMounted, ref, toRefs} from 'vue'
  import {GetDictItems} from '@/api/dictonary'

  const props = defineProps(['type', 'value', 'code'])
  const emit = defineEmits(['update:value'])
  const {element, value, code} = toRefs(props)
  const itemArray = ref(null)

  function handleUpdate(currentValue) {
    emit('update:value', currentValue)
  }

  onMounted(() => {
    GetDictItems(code.value).then(response => {
      itemArray.value = response
    })
  })
</script>

<style scoped>

</style>
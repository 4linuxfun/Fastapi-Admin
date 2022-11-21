<template>
  <!--数据字典自动带出组件。通过提供的URL获取信息，并根据需要选择相应的组件进行展示-->
  <template v-if="type==='select'">
    <el-select v-model="modelValue" @change="handleUpdate">
      <el-option v-for="item in itemArray" :key="item.value" :label="item.label" :value="item.value"/>
    </el-select>
  </template>

  <template v-else-if="type === 'switch'">
    <el-switch v-model="modelValue" @change="handleUpdate"
               style="--el-switch-on-color: #13ce66; --el-switch-off-color: #ff4949"/>
  </template>

  <template v-else-if="type === 'checkbox'">
    <el-checkbox-group v-model="modelValue" @change="handleUpdate">
      <el-row :gutter="20">
        <el-col v-for="item in itemArray" :key="item.value" :span="colSpan">
          <el-checkbox :label="item.value" style="display: flex">{{ item.label }}</el-checkbox>
        </el-col>
      </el-row>
    </el-checkbox-group>
  </template>

</template>

<script setup>
  import {onMounted, ref, toRefs} from 'vue'
  import {GetDictItems} from '@/api/dictonary'

  const props = defineProps({
    //选择框类型
    type: {
      type: String,
      validator(value) {
        return ['select', 'switch', 'checkbox'].includes(value)
      }
    },
    //数据字典对应编码
    code: {
      type: String,
      required: true
    },
    //checkbox时用于对应列数
    col: {
      type: Number,
      default: 2
    },
    //绑定的值
    modelValue: {
      required: true
    }
  })
  const emit = defineEmits(['update:modelValue'])
  const {type, code, col, modelValue} = toRefs(props)
  const itemArray = ref(null)
  const colSpan = 24 / col.value

  function handleUpdate(currentValue) {
    emit('update:modelValue', currentValue)
  }

  onMounted(() => {
    GetDictItems(code.value).then(response => {
      itemArray.value = response
    })
  })
</script>

<style scoped>

</style>
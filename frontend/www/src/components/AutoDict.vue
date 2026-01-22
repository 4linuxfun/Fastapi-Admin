<template>
  <!--数据字典自动带出组件。通过提供的URL获取信息，并根据需要选择相应的组件进行展示-->
  <template v-if="loading">
    <div>Loading...</div>
  </template>

  <template v-if="dictType === 'select'">
    <el-select v-model="modelValue" @change="handleUpdate">
      <el-option v-for="item in itemArray" :key="item.value" :label="item.label" :value="item.value" />
    </el-select>
  </template>

  <template v-if="dictType === 'select+'">
    <el-select v-model="modelValue" :filterable="true" :allow-create="true" @change="handleUpdate">
      <el-option v-for="item in itemArray" :key="item.value" :label="item.label" :value="item.value" />
    </el-select>
  </template>

  <template v-else-if="dictType === 'switch'">
    <el-switch v-model="modelValue" @change="handleUpdate"
      style="--el-switch-on-color: #13ce66; --el-switch-off-color: #ff4949" />
  </template>

  <template v-else-if="dictType === 'checkbox'">
    <el-checkbox v-model="checkAll" :indeterminate="isIndeterminate" @change="handleCheckAllChange">全选</el-checkbox>
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
import { onMounted, ref, toRefs, watch, nextTick } from 'vue'
import { GetDictItems } from '@/api/dictonary'
import { useDictStore } from "@/stores/dict";

const props = defineProps({
  //选择框类型
  dictType: {
    type: String,
    validator(value) {
      return ['select', 'select+', 'switch', 'checkbox'].includes(value)
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
const { dictType, code, col, } = toRefs(props)
const modelValue = ref(props.modelValue)
const itemArray = ref(null)
const colSpan = 24 / col.value
const checkAll = ref(false)
const isIndeterminate = ref(true)
const distStore = useDictStore()
const loading = ref(false)

let allItems = []

function handleUpdate(currentValue) {
  if (dictType.value === 'checkbox') {
    const checkedCount = currentValue.length
    checkAll.value = checkedCount === allItems.length
    isIndeterminate.value = checkedCount > 0 && checkedCount < allItems.length
  }
  modelValue.value = currentValue
}

function handleCheckAllChange(val) {
  if (val) {
    modelValue.value = allItems
  } else {
    modelValue.value = []
  }
  isIndeterminate.value = false
}

watch(modelValue, (newVal) => {
  emit('update:modelValue', newVal)
})

onMounted(async () => {
  try {
    itemArray.value = await distStore.getDictItems(code.value)
    console.log(itemArray.value)
    if (dictType.value === 'checkbox') {
      itemArray.value.forEach((item) => {
        allItems.push(item['value'])
      })
    }
  } finally {
    loading.value = false
    await nextTick()
  }

})
</script>

<style scoped></style>
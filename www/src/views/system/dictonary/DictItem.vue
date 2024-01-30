<template>
  <!--  字典列表页面，用于显示、查询、新增、编辑字典元素-->
  <el-drawer v-model="visible" :title="`字典名称：${dictName}`" size="30%" destroy-on-close>
    <el-row>
      <el-row>
        <el-form :model="search" :inline="true" ref="searchRef">
          <el-form-item label="名称" prop="label">
            <el-input style="width: 100px" v-model="search.label"/>
          </el-form-item>
          <el-form-item label="状态" prop="enable">
            <el-select v-model="search.enable" style="width: 100px">
              <el-option label="正常" :value="1"/>
              <el-option label="禁用" :value="0"/>
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">
              <el-icon>
                <Search/>
              </el-icon>
              搜索
            </el-button>
            <el-button type="primary" @click="handleReset">
              <el-icon>
                <RefreshRight/>
              </el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </el-row>
    </el-row>


    <el-row>
      <el-button type="primary" :icon="Plus" @click="handleAdd">新增</el-button>
    </el-row>

    <el-table :data="tableData" border style="margin-top: 10px">
      <el-table-column label="名称" prop="label"/>
      <el-table-column label="数据值" prop="value"/>
      <el-table-column label="是否启用" prop="enable">
        <template #default="scope">
          <el-switch v-model="scope.row.enable"
                     @change="handleUpdate(scope.row)"
                     style="--el-switch-on-color: #13ce66; --el-switch-off-color: #ff4949"/>
        </template>
      </el-table-column>
      <el-table-column label="操作">
        <template #default="scope">
          <el-button text type="primary"
                     class="item_button"
                     @click="handleEdit(scope.row)" :icon="Edit"/>
          <el-divider direction="vertical"/>
          <el-popconfirm title="确定要删除此元素吗？" @confirm="handleDel(scope.row.id)">
            <template #reference>
              <el-button text type="danger"
                         class="item_button"
                         :icon="Delete"/>
            </template>
          </el-popconfirm>

        </template>
      </el-table-column>
    </el-table>

    <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total" background
                   layout="total,prev,pager,next,sizes,jumper"
                   style="margin-top: 10px;"
    />

    <add-item ref="addItemDialogRef" @success="freshCurrentPage"/>

  </el-drawer>
</template>

<script setup>

  import {Plus, Edit, Delete} from '@element-plus/icons-vue'
  import usePagination from '@/composables/usePagination'
  import {ref, watch} from 'vue'
  import AddItem from '@/views/system/dictonary/AddItem'
  import {DelDictItem, PutDictItem} from '@/api/dictonary'
  import {ElNotification} from 'element-plus'

  const dictId = ref(null)
  const dictName = ref(null)
  const visible = ref(false)
  const addItemDialog = ref(false)
  const selectItem = ref(null)
  const searchRef = ref(null)
  const addItemDialogRef = ref(null)

  let searchForm = {
    dict_id: null,
    label: null,
    value: null,
    enable: null
  }


  const {
    search,
    tableData,
    currentPage,
    pageSize,
    orderModel,
    total,
    freshCurrentPage,
    handleSearch
  } = usePagination('/api/dict/item/search', searchForm)

  function handleAdd() {
    addItemDialogRef.value.add(dictId.value)
  }

  function handleReset() {
    searchRef.value.resetFields()
  }

  function handleEdit(dictItem) {
    addItemDialogRef.value.edit(dictItem)
  }

  function handleDel(itemId) {
    DelDictItem(itemId).then(() => {
          ElNotification({
            title: 'success',
            message: '字典元素删除成功',
            type: 'success'
          })
          freshCurrentPage()
        }
    )

  }

  async function handleUpdate(item) {
    try {
      await PutDictItem(item)
      ElNotification({
        title: 'success',
        message: '字典元素更新成功',
        type: 'success'
      })
      await freshCurrentPage()
    } catch (error) {
      ElNotification({
        title: 'error',
        message: '字典元素更新失败',
        type: 'error'
      })
    }

  }

  function edit(dict) {
    search.dict_id = dict.id
    dictId.value = dict.id
    dictName.value = dict.name
    visible.value = true
    handleSearch()
  }

  watch(addItemDialog, (newValue) => {
    if (newValue === false) {
      freshCurrentPage()
    }

  })

  defineExpose({edit})

</script>

<style scoped>
.item_button {
  padding: 0;
}
</style>
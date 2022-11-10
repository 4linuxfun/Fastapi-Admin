<template>
  <!--  字典列表页面，用于显示、查询、新增、编辑字典元素-->
  <el-row>
    <el-row>
      <el-form v-model="search" :inline="true">
        <el-form-item label="名称">
          <el-input style="width: 100px" v-model="search.name"/>
        </el-form-item>
        <el-form-item label="状态">
          <el-input style="width: 100px" v-model="search.enable"/>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon>
              <Search/>
            </el-icon>
            搜索
          </el-button>
          <el-button>重置</el-button>
        </el-form-item>
      </el-form>
    </el-row>
  </el-row>


  <el-row>
    <el-button type="primary" :icon="Plus" @click="handleAdd">新增</el-button>
  </el-row>


  <el-table :data="tableData" border style="margin-top: 10px">
    <el-table-column label="名称" prop="name"/>
    <el-table-column label="数据值" prop="data"/>
    <el-table-column label="操作">
      <template #default="scope">
        <el-button text type="primary"
                   class="item_button"
                   @click="handleEdit(scope.row)" :icon="Edit">编辑</el-button>
        <el-divider direction="vertical"/>
        <el-popconfirm title="确定要删除此元素吗？" @confirm="handleDel(scope.row.id)">
          <template #reference>
            <el-button text type="danger"
                       class="item_button"
                       :icon="Delete">删除</el-button>
          </template>
        </el-popconfirm>

      </template>
    </el-table-column>
  </el-table>

  <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total" background
                 layout="total,prev,pager,next,sizes,jumper"
                 style="margin-top: 10px;"
  />

  <el-dialog v-model="addItemDialog" width="30%" destroy-on-close>
    <add-item :item="selectItem" v-model:visible="addItemDialog"/>
  </el-dialog>
</template>

<script setup>

  import {Plus, Edit, Delete} from '@element-plus/icons-vue'
  import usePagination from '@/composables/usePagination'
  import {ref, watch} from 'vue'
  import AddItem from '@/views/system/dictonary/AddItem'
  import {DelDictItem} from '@/api/dictonary'
  import {ElNotification} from 'element-plus'

  const props = defineProps(['id'])
  const addItemDialog = ref(false)
  const selectItem = ref(null)

  let searchForm = {
    dict_id: props.id,
    name: null,
    data: null,
    type: {
      dict_id: 'eq',
      name: 'like',
      code: 'like',
    }
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
    selectItem.value = {
      id: null,
      name: null,
      data: null,
      desc: null,
      sort: null,
      enable: true,
      dict_id: props.id
    }
    addItemDialog.value = true
  }

  function handleEdit(dictItem) {
    selectItem.value = dictItem
    addItemDialog.value = true
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

  watch(addItemDialog, (newValue) => {
    if (newValue === false) {
      freshCurrentPage()
    }

  })

</script>

<style scoped>
.item_button{
  padding: 0;
}
</style>
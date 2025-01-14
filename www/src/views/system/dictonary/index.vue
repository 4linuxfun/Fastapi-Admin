<template>
  <el-row>
    <el-form inline :model="search" ref="searchRef">
      <el-form-item label="字典名称" prop="name">
        <el-input v-model="search.name"/>
      </el-form-item>
      <el-form-item label="字典编号" prop="code">
        <el-input v-model="search.code"/>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
        <el-button type="primary" @click="handleReset">
          <el-icon>
            <RefreshRight/>
          </el-icon>
          重置
        </el-button>
      </el-form-item>
    </el-form>
  </el-row>
  <el-row>
    <el-button type="primary" :icon="Plus" @click="handleAdd">添加</el-button>
    <el-button type="primary" :icon="DocumentCopy">导出</el-button>
    <el-button type="primary" :icon="DocumentAdd">导入</el-button>
    <el-button type="primary" :icon="Refresh">刷新缓存</el-button>
    <el-button type="primary" :icon="Delete">回收站</el-button>
  </el-row>

  <el-table :data="tableData" border style="margin-top: 10px"
            :header-cell-style="{background:'#eef1f6',color:'#606266'}">
    <el-table-column type="index" label="#"/>
    <el-table-column label="字典名称" prop="name"/>
    <el-table-column label="字典编号" prop="code"/>
    <el-table-column label="描述" prop="desc"/>
    <el-table-column label="操作">
      <template #default="scope">
        <el-button text type="primary" style="padding: 0" :icon="EditPen" @click="handleEdit(scope.row)">操作
        </el-button>
        <el-divider direction="vertical"/>
        <el-button text type="primary" style="padding: 0" :icon="Setting" @click="handleItem(scope.row)">字典配置
        </el-button>
        <el-divider direction="vertical"/>
        <el-button text type="danger" style="padding: 0" :icon="Delete" @click="handleDel(scope.row)">删除</el-button>
      </template>
    </el-table-column>
  </el-table>

  <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total" background
                 layout="total,prev,pager,next,sizes,jumper"
                 style="margin-top: 10px;"
  />

  <el-dialog v-model="addDialog" width="30%" :title="dialogTitle" destroy-on-close>
    <add-dict :dict="selectDict" v-model:visible="addDialog"/>
  </el-dialog>

  <dict-item ref="dictItemRef"/>

</template>

<script>
  export default {
    name: '数据字典'
  }
</script>

<script setup>
  import {
    Search,
    Plus,
    DocumentCopy,
    DocumentAdd,
    Refresh,
    Delete,
    EditPen,
    Setting
  } from '@element-plus/icons-vue'
  import {onMounted, ref, watch} from 'vue'
  import usePagination from '@/composables/usePagination'
  import AddDict from '@/views/system/dictonary/AddDict'
  import DictItem from '@/views/system/dictonary/DictItem'
  import {DelDict} from '@/api/dictonary'
  import {ConfirmDel} from '@/utils/request'


  const addDialog = ref(false)
  const dialogTitle = ref(null)
  const selectDict = ref(null)
  const searchRef = ref(null)
  const dictItemRef = ref(null)

  const searchForm = {
    name: null,
    code: null,
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
  } = usePagination('/api/dict/search', searchForm)

  function handleAdd() {
    dialogTitle.value = '添加数据字典'
    selectDict.value = {
      id: null,
      name: null,
      code: null,
      desc: null
    }
    addDialog.value = true
  }

  function handleReset() {
    searchRef.value.resetFields()
    handleSearch()
  }

  /*
   * 编辑数据字典
   */
  function handleEdit(dict) {
    dialogTitle.value = '编辑数据字典'
    selectDict.value = dict
    console.log(dict)
    addDialog.value = true
  }

  /*
  * 字典元素配置
   */
  function handleItem(dict) {
    dictItemRef.value.edit(dict)
  }

  /*
  *删除字典
   */
  async function handleDel(dict) {
    await ConfirmDel('删除字典会一起删除对应的元素', DelDict, dict.id)
    await freshCurrentPage()
  }

  watch(addDialog, (newValue) => {
    if (newValue === false) {
      freshCurrentPage()
    }
  })

  onMounted(() => {
    handleSearch()
  })

</script>

<style scoped>
</style>
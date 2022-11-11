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
        <el-button text type="danger" style="padding: 0" :icon="Delete">删除</el-button>
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

  <el-drawer v-model="itemDrawer" title="字典列表" size="30%" destroy-on-close>
    <dict-item :id="selectDict.id"/>
  </el-drawer>

</template>

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

  // const tableData = ref([
  //   {name: '测试', code: '1111', des: 'dddddddd'},
  //   {name: 'cccc', code: '22222', des: 'sssssss'}
  // ])
  const addDialog = ref(false)
  const itemDrawer = ref(false)
  const dialogTitle = ref(null)
  const selectDict = ref(null)
  const searchRef = ref(null)

  const searchForm = {
    name: null,
    code: null,
    type: {
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
  } = usePagination('/api/dict/search', searchForm)

  function handleAdd() {
    dialogTitle.value = '添加数据字典'
    selectDict.value = {
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

  function handleEdit(dict) {
    dialogTitle.value = '编辑数据字典'
    selectDict.value = dict
    console.log(dict)
    addDialog.value = true
  }

  function handleItem(dict) {
    selectDict.value = dict
    itemDrawer.value = true
  }

  watch(addDialog,(newValue)=>{
    if(newValue === false){
      freshCurrentPage()
    }
  })

  onMounted(() => {
    freshCurrentPage()
  })

</script>

<style scoped>
.custom_pagination {
  margin-top: 10px;
  padding-left: 0;
}
</style>
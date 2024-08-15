<template>
  <el-row style="background: white;padding: 20px;">
    <el-form>
      <el-form-item label="模板名称">
        <el-input/>
      </el-form-item>
    </el-form>
  </el-row>

  <div style="background: white;padding: 20px;margin-top: 10px">

    <el-row justify="space-between">
      <el-col :span="12">
        <span>模板列表</span>
      </el-col>
      <el-col :span="12" style="text-align: right">
        <el-button type="primary" size="large" :icon="Plus" @click="addPlaybookRef.add()">新建模板</el-button>
      </el-col>

    </el-row>
    <el-row>
      <el-table :data="tableData" border style="margin-top: 10px">
        <el-table-column label="模板名称" prop="name"/>
        <el-table-column label="描述信息" prop="desc"/>
        <el-table-column label="操作">
          <template #default="scope">
            <el-button link type="primary" @click="addPlaybookRef.edit(scope.row.id)">编辑</el-button>
            <el-button link type="primary" @click="">复制</el-button>
            <el-button link type="danger" @click="handleDel(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total" background
                     layout="total,prev,pager,next,sizes,jumper"
                     style="margin-top: 10px;"
      />
    </el-row>
  </div>

  <add-playbook ref="addPlaybookRef" @close="freshCurrentPage"/>

</template>
<script>
  export default {
    name: '脚本管理'
  }
</script>

<script setup>
  import {ref, reactive, onMounted} from 'vue'
  import {Plus} from '@element-plus/icons-vue'
  import AddPlaybook from '@/views/jobs/playbook/AddPlaybook.vue'
  import usePagination from '@/composables/usePagination.js'
  import {DelPlaybook} from '@/api/playbook.js'
  import {ConfirmDel} from '@/utils/request.js'

  const addPlaybookRef = ref(null)

  const searchForm = {
    name: null
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
  } = usePagination('/api/playbook/search', searchForm)

  async function handleDel(id) {
    try {
      await ConfirmDel('确定删除模板吗？', DelPlaybook, id)
    } catch (e) {
      console.log(e)
    }
    await freshCurrentPage()
  }

  onMounted(() => {
    handleSearch()
  })

</script>

<style scoped>

</style>
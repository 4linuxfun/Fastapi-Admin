<template>
  <el-row>
    <el-form :model="search" :inline="true">
      <el-form-item label="标签">
        <el-input v-model="search.tags"/>
      </el-form-item>
      <el-form-item label="方法">
        <el-input v-model="search.method"/>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
      </el-form-item>
    </el-form>
  </el-row>
  <div style="padding-top:10px">
    <el-table :data="tableData" border stripe :header-cell-style="{background:'#eef1f6',color:'#606266'}">
      <el-table-column type="index" label="#"/>
      <el-table-column prop="tags" label="标签" align="center"/>
      <el-table-column prop="path" label="接口地址" align="center"/>
      <el-table-column prop="method" label="方法" align="center"/>
      <el-table-column prop="summary" label="描述" align="center"/>
    </el-table>
    <!-- <el-pagination v-model:current-page="currentPage" background :page-sizes="[10,20,50,100]"
      v-model:page-size="pageSize" layout="total,sizes,prev,pager,next,jumper" :total="total" prev-text="上一页"
      next-text="下一页"></el-pagination> -->
    <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total" background
                   layout="prev,pager,next"
                   prev-text="上一页" next-text="下一页"
    />
  </div>
</template>

<script>
  import {
    reactive,
    ref
  } from 'vue'
  import usePagination from '@/composables/usePagination'
  import {GetSysApis} from '@/api/sysapi'

  export default {
    name: 'SystemApis',
    setup() {
      const formData = reactive({})
      const formSchema = reactive({})
      const dialogVisible = ref(false)
      const selectUser = reactive({})
      const searchForm = {
        tags: null,
        path: null,
        method: null,
        summary: null,
        type: {
          tags: 'r_like',
          path: 'a_like',
          method: 'eq',
          summary: 'a_like',
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
      } = usePagination('/api/sysapis/search', searchForm)

      return {
        formData,
        formSchema,
        search,
        dialogVisible,
        tableData,
        selectUser,
        pageSize,
        currentPage,
        orderModel,
        total,
        freshCurrentPage,
        handleSearch
      }
    },
    methods: {
      addApis() {
        console.log('add api button clicks')
        GetForm('Api').then((response) => {
          console.log(response)
        })
      },

    },
  }
</script>

<style scoped>

</style>
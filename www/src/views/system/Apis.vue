<template>
  <el-row style="width:300px" :gutter="5">
    <el-col :span="18">
      <el-input v-model="search" placeholder="搜索" clearable>
        <template #append>
          <el-button @click="handleSearch">
            <el-icon>
              <search/>
            </el-icon>
          </el-button>
        </template>
      </el-input>
    </el-col>
  </el-row>
  <div style="padding-top:10px">
    <vxe-table :data="tableData" align="center" border="full" size="medium" :row-config="{isHover:true}">
      <vxe-column type="seq" width="60"></vxe-column>
      <vxe-column field="name" title="用户名"></vxe-column>
      <vxe-column field="email" title="邮箱"></vxe-column>
      <vxe-column fixed="avatar" title="头像"></vxe-column>
      <vxe-column field="enable" title="状态">
        <template #default="scope">
          <el-tag effect="dark" :type="scope.row.enable === 1?'success':'danger'">
            {{ scope.row.enable === 1 ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </vxe-column>
      <vxe-column title="操作">
        <template #default="scope">
          <el-button type="primary" size="small" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button type="danger" size="small" @click="handleDel(scope.row.id,scope.row.name)">删除</el-button>
        </template>
      </vxe-column>
    </vxe-table>
    <!-- <el-pagination v-model:current-page="currentPage" background :page-sizes="[10,20,50,100]"
      v-model:page-size="pageSize" layout="total,sizes,prev,pager,next,jumper" :total="total" prev-text="上一页"
      next-text="下一页"></el-pagination> -->
    <vxe-pager v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total" align="left"
               :layouts="['PrevJump', 'PrevPage', 'JumpNumber', 'NextPage', 'NextJump', 'Sizes', 'FullJump', 'Total']">
    </vxe-pager>
  </div>
</template>

<script>
  export default {
    name: 'SystemApis'
  }
</script>

<style scoped>

</style>
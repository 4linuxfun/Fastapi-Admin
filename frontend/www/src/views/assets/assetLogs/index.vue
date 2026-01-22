<template>
  <div>
    <!-- 查询表单 -->
    <el-row>
      <el-form :model="searchForm" ref="searchFormRef" :inline="true">
        <el-form-item label="资产编号">
          <el-input v-model="searchForm.asset_code" placeholder="请输入资产编号" clearable />
        </el-form-item>
        <el-form-item label="资产名称">
          <el-input v-model="searchForm.asset_name" placeholder="请输入资产名称" clearable />
        </el-form-item>
        <el-form-item label="操作人">
          <el-input v-model="searchForm.operator" placeholder="请输入操作人" clearable />
        </el-form-item>
        <el-form-item label="操作类型">
          <el-select v-model="searchForm.action" placeholder="请选择操作类型" clearable>
            <el-option label="资产录入" value="资产录入" />
            <el-option label="资产编辑" value="资产编辑" />
            <el-option label="资产领用" value="资产领用" />
            <el-option label="资产退回" value="资产退回" />
            <el-option label="资产转移" value="资产转移" />
            <el-option label="资产报废" value="资产报废" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD HH:mm:ss"
            @change="handleDateRangeChange"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch" :loading="loading" :icon="Search">查询</el-button>
          <el-button @click="handleReset" :icon="Refresh">重置</el-button>
        </el-form-item>
      </el-form>
    </el-row>

    <!-- 资产日志表格 -->
    <el-table
      :data="tableData"
      border
      stripe
      v-loading="loading"
      style="width: 100%;margin-top: 10px;"
      :header-cell-style="{ background: '#eef1f6', color: '#606266' }"
    >
      <el-table-column label="#" type="index" width="50" />
      <el-table-column prop="asset_code" label="资产编号" align="center" width="120" />
      <el-table-column prop="asset_name" label="资产名称" align="center" width="150" />
      <el-table-column prop="category_name" label="资产分类" align="center" width="120" />
      <el-table-column prop="location_name" label="存放位置" align="center" width="120" />
      <el-table-column prop="department_name" label="所属部门" align="center" width="120" />
      <el-table-column prop="operator" label="操作人" align="center" width="100" />
      <el-table-column prop="action" label="操作类型" align="center" width="100">
        <template #default="scope">
          <el-tag :type="getActionTagType(scope.row.action)">
            {{ scope.row.action }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="details" label="操作详情" align="center" min-width="200" />
      <el-table-column prop="timestamp" label="操作时间" align="center" width="180">
        <template #default="scope">
          {{ formatDateTime(scope.row.timestamp) }}
        </template>
      </el-table-column>
    </el-table>
    
    <el-pagination 
      v-model:current-page="currentPage" 
      v-model:page-size="pageSize" 
      :page-sizes="[10, 20, 50, 100]"
      :total="total" 
      background
      layout="total,prev,pager,next,sizes,jumper" 
      style="margin-top: 10px;" 
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { Search, Refresh } from '@element-plus/icons-vue';
import { SearchAssetLogs } from '@/api/assets';

defineOptions({
  name: "资产日志",
});

// 响应式数据
const loading = ref(false);
const tableData = ref([]);
const currentPage = ref(1);
const pageSize = ref(20);
const total = ref(0);
const dateRange = ref([]);

// 搜索表单
const searchForm = reactive({
  asset_id: null,
  asset_code: "",
  asset_name: "",
  operator: "",
  action: "",
  category_id: null,
  location_id: null,
  department_id: null,
  start_time: null,
  end_time: null,
});

const searchFormRef = ref();

// 处理日期范围变化
const handleDateRangeChange = (value) => {
  if (value && value.length === 2) {
    searchForm.start_time = value[0];
    searchForm.end_time = value[1];
  } else {
    searchForm.start_time = null;
    searchForm.end_time = null;
  }
};

// 获取操作类型标签样式
const getActionTagType = (action) => {
  const typeMap = {
    '资产录入': 'success',
    '资产编辑': 'warning',
    '资产领用': 'primary',
    '资产退回': 'info',
    '资产转移': 'warning',
    '资产报废': 'danger'
  };
  return typeMap[action] || 'default';
};

// 格式化日期时间
const formatDateTime = (dateTime) => {
  if (!dateTime) return '';
  return new Date(dateTime).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
};

// 搜索日志
const handleSearch = async () => {
  loading.value = true;
  try {
    const searchData = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: { ...searchForm }
    };

    const response = await SearchAssetLogs(searchData);
    if (response.code === 200) {
      tableData.value = response.data.data;
      total.value = response.data.total;
    } else {
      ElMessage.error(response.message || '查询失败');
    }
  } catch (error) {
    console.error('Search asset logs error:', error);
    ElMessage.error('查询失败，请稍后重试');
  } finally {
    loading.value = false;
  }
};

// 重置搜索
const handleReset = () => {
  searchFormRef.value?.resetFields();
  Object.keys(searchForm).forEach(key => {
    if (key === 'start_time' || key === 'end_time' || key === 'asset_id' || key === 'category_id' || key === 'location_id' || key === 'department_id') {
      searchForm[key] = null;
    } else {
      searchForm[key] = "";
    }
  });
  dateRange.value = [];
  currentPage.value = 1;
  handleSearch();
};

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val;
  currentPage.value = 1;
  handleSearch();
};

const handleCurrentChange = (val) => {
  currentPage.value = val;
  handleSearch();
};

// 组件挂载时加载数据
onMounted(() => {
  handleSearch();
});
</script>

<style>
/* 移除自定义样式，使用默认样式保持与其他页面一致 */
</style>
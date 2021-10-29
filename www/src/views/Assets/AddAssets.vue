<template>
    <el-container>
        <el-header class="search-header">
          <div style="float: left">
            资产类型：
            <div style="display:inline-block">
                <el-input v-model="assType" placeholder="请输入资产名"></el-input>
            </div>
            资产型号：
            <div style="display:inline-block">
                <el-input v-model="assName" placeholder="请输入型号"></el-input>
            </div>
            <div style="display:inline-block">
              <el-button @click="clickEvent" type="primary" icon="el-icon-search">搜索</el-button>
            </div>
          </div>
          
        </el-header>
        <!-- 表格内容 -->
        <el-main class="table-style">
          <el-table :data="tableData" border highlight-current-row>
            <el-table-column 
              prop="date"
              label="日期"
              width="180"
              sortable>
            </el-table-column>
            <el-table-column 
              prop="name"
              label="姓名"
              width="180">
            </el-table-column>
            <el-table-column
              prop="address"
              label="地址">
            </el-table-column>
            <el-table-column label="操作">
              <template #default="scope">
                <el-button size="mini" @click="handleShow(scope.$index,scope.row)">详情</el-button>
              </template>
            </el-table-column>

          </el-table>
          <!-- 详情页面信息 -->
          <el-dialog
            v-model="dialogVisible"
            title="详细"
            width="70%">
            <div v-for="(value,name,index) in selected.row" :key="index">
                <details-dialog :title="name" :message="value" style="line-height: normal"></details-dialog>
            </div>
            
            <template #footer>
              <el-button size="mini">更新</el-button>
            </template>
          </el-dialog>
        </el-main>
    </el-container>
</template>

<script>


export default {

  data() {
    return {
      assType: "",
      assName: "",
      click: 0,
      dialogVisible:false,
      selected: {index:'',row:''},
      tableData: [
        {
          date: "2016-05-02",
          name: "王小虎",
          address: "上海市普陀区金沙江路 1518 弄",
          telephone: 15556677667,
          id: 333333333,
        },
        {
          date: "2016-05-04",
          name: "王小虎",
          address: "上海市普陀区金沙江路 1517 弄",
        },
        {
          date: "2016-05-01",
          name: "王小虎",
          address: "上海市普陀区金沙江路 1519 弄",
        },
        {
          date: "2016-05-03",
          name: "王小虎",
          address: "上海市普陀区金沙江路 1516 弄",
        },
      ],
    };
  },
  methods: {
    clickEvent() {
      this.click += 1;
    },
    handleShow(index, row) {
      console.log(index, row);
      this.dialogVisible=true;
      this.selected.row = row;
      this.selected.index = index;
    },
  },
};
</script>

<style>
.search-header {
  display: inline-block;
}
.table-style {
  padding: 0;
  background-color: aqua;
  line-height: 0;
}
</style>
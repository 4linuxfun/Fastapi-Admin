<template lang="">
        
        <div>
            <div><p>类型：</p></div><el-input :size="medium" v-model="search" placeholder="请输入查询内容"></el-input>
        </div>
                
    
    <!-- <el-row>
        <el-col :span="24">
            内容页面
        </el-col>
    </el-row> -->

</template>

<script>
export default {
  data() {
    return {
      search: "",
    };
  },
};
</script>

<style scoped>
.grid-content {
  border-radius: 4px;
  line-height: 1.5;
  /* min-height: 10px; */
  /* height:50px; */
}
.bg-purple-dark {
  background: #99a9bf;
}
</style>
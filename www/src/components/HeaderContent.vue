<template lang="">
    <div>
        <el-row justify="end">
            <el-col :span="4"><div>header</div></el-col>
            <el-col :span="4">
                <div>
                    <el-button circle @click="logOut">退出</el-button>
                </div>
            </el-col>
        </el-row>
    </div>
</template>
<script>
import {ElMessage, ElMessageBox} from 'element-plus';

export default {
  name: "HeaderContent",
  methods: {
    logOut() {
      console.log("click logout button");
      ElMessageBox.confirm('确定退出系统吗？','提示',{
          confirmButtonText:'是',
          cancelButtonText:'否',
          type:'warning'
      }).then(()=>{
          this.$store.dispatch('logOut');
          this.$router.push('/login');
          ElMessage({
              type:'success',
              message:'退出成功！'
          });
      }).catch(()=>{
          ElMessage({
              type:'info',
              message:'取消退出'
          });
      });
    
    },
  },
};
</script>
<style lang="">
</style>
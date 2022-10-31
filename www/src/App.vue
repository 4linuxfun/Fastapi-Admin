<template>
  <div style="height: 100%">
    <router-view />
  </div>
</template>

<script>

  export default {
    name: 'App',

  }
</script>

<style>
html, body, #app, .el-container {
  /*设置内部填充为0，几个布局元素之间没有间距*/
  padding: 0px;
  /*外部间距也是如此设置*/
  margin: 0px;
  /*统一设置高度为100%*/
  height: 100%;
}

.el-header, .el-footer {
  background-color: #B3C0D1;
  color: #333;
  text-align: center;
  line-height: 60px;
}

.el-aside {
  background-color: #073d7a;
  color: rgb(250, 245, 245);
  /* padding-left:10px; */
  /* text-align: center;
  line-height: 200px; */
}

.el-main {
  color: #333;
  text-align: center;
  /* line-height: 160px; */
  padding: 0;
}

body > .el-container {
  margin-bottom: 40px;
}

.el-container:nth-child(5) .el-aside,
.el-container:nth-child(6) .el-aside {
  line-height: 260px;
}

.el-container:nth-child(7) .el-aside {
  line-height: 320px;
}
</style>

<template>
    <router-view/>
</template>

<script>

  export default {
    name: 'App',

  }
</script>

<style>
html, body {
  height: 100%
}

#app {
  height: 100%
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
</style>

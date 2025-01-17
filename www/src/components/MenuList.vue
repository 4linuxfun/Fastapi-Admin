<template>
  <el-menu
      class="el-menu-vertical-demo"
      style="--el-menu-bg-color: #1c1919;--el-menu-text-color: #ffffff;--el-menu-active-color: #3885d4;--el-menu-hover-bg-color:#3885d4 "
      router
      :collapse="collapseStore.collapse"
      unique-opened
      @open="handleOpen"
      @close="handleClose">
    <div style="height: 50px;background-color: #1c1919;">
      <!--      菜单折叠只显示图标-->
      <div class="header-font" v-if="!collapseStore.collapse">FastAdmin管理平台</div>
    </div>
    <el-menu-item index="/">首页</el-menu-item>
    <template v-for="item in menuList" :key="item.name">
      <!-- 有子菜单时处理逻辑 -->
      <el-sub-menu v-if="item.children.length>0" :index="item.path">
        <template #title>
          <el-icon v-if="item.icon">
            <component :is="item.icon"/>
          </el-icon>
          <span>{{ item.name }}</span>
        </template>
        <template v-if="item.children.length >0">
          <el-menu-item v-for="(children,index) in item.children" :key="index"
                        :index="item.path + '/' + children.path">
            <el-icon v-if="children.icon">
              <component :is="children.icon"/>
            </el-icon>
            <span>{{ children.name }}</span>
          </el-menu-item>
        </template>
      </el-sub-menu>
      <!-- 无子菜单时处理逻辑 -->
      <el-menu-item v-else :index="item.path">
        <el-icon v-if="item.icon">
          <component :is="item.icon"/>
        </el-icon>
        <span>{{ item.name }}</span>
      </el-menu-item>
    </template>

  </el-menu>
</template>

<script setup>
  import {useStore} from '@/stores'
  import {computed, ref} from 'vue'
  import {useCollapseStore} from '@/stores/collapse.js'

  const collapseStore = useCollapseStore()
  const userStore = useStore()

  const menuList = computed(() => {
    return userStore.asyncRoutes
  })

  function handleOpen(key, keyPath) {
    console.log(key, keyPath)
  }

  function handleClose(key, keyPath) {
    console.log(key, keyPath)
  }

</script>

<style>
.header-font {
  font-size: large;
  background-color: #1c1919;
  color: #ffffff;
  text-align: center;
  padding: 10px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.el-menu-vertical-demo {
  min-height: 100%;
}

.el-menu-vertical-demo:not(.el-menu--collapse) {
  width: 200px;
}
</style>
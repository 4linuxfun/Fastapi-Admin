<template>
  <div style="height: 100%">
    <el-container style="height: 100%">
      <el-aside class="aside-menu" width="auto">
        <menu-list></menu-list>
      </el-aside>
      <el-container style="height: 100%">
        <el-header style="--el-header-padding: 0 10px" height="50px">
          <header-content></header-content>
        </el-header>
        <el-main style="padding: 0">
          <el-tabs style="border-bottom: 0;" v-model="currentTab" type="border-card"
                   @tab-click="tabClick"
                   @tab-remove="tabRemove">
            <el-tab-pane v-for="tab in allTabs" :key="tab.name" :label="tab.name" :name="tab.name" :closable="tab.name !== '首页'">
              <div class="user-container">
                <div style="background-color:white;height: 100%;padding: 10px">
                  <router-view v-slot="{Component}">
                    <keep-alive :include="cacheTabs">
                      <component :is="Component"/>
                    </keep-alive>
                  </router-view>
                </div>
              </div>
              <!--详见：https://router.vuejs.org/zh/guide/migration/index.html#router-view-%E3%80%81-keep-alive-%E5%92%8C-transition-->
            </el-tab-pane>
          </el-tabs>


        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
  import {useTabsStore} from '@/stores/tabs'
  import {watch} from 'vue'
  import {storeToRefs} from 'pinia'

  const tabStore = useTabsStore()
  const {currentTab, allTabs, cacheTabs, tabsList} = storeToRefs(tabStore)
  const {addTab, tabRemove, tabClick} = tabStore

  console.log(tabsList.value)
  watch(currentTab, (newValue, oldValue) => {
    console.log('current Tab changed:', newValue)
  })
</script>

<style>
.user-container {
  padding: 10px 20px;
  height: calc(100% - 60px);
  background-color: rgb(245, 245, 245);
}

.el-tabs--border-card > .el-tabs__content {
  padding: 0;
}

.el-tabs--border-card > .el-tabs__header > .el-tabs__nav-wrap > .el-tabs__nav-scroll > .el-tabs__nav > .el-tabs__item.is-active {
  background-color: rgb(245, 245, 245) !important;
}
</style>
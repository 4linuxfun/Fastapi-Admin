<template>
  <div style="height: 100%">
    <el-container style="height: 100%">
      <el-header>
        <header-content></header-content>
      </el-header>
      <el-container style="height: 100%">
        <el-aside width="200px">
          <menu-list></menu-list>
        </el-aside>
        <el-main style="padding: 0px">
          <el-tabs style="border-bottom: 0" v-model="currentTab" type="border-card" closable @tab-click="tabClick" @tab-remove="tabRemove">
            <el-tab-pane v-for="tab in allTabs" :key="tab.name" :label="tab.name" :name="tab.name">
            </el-tab-pane>
          </el-tabs>

          <div class="main_style">
             <router-view v-slot="{Component}">
            <keep-alive :include="cacheTabs">
              <component :is="Component"/>
            </keep-alive>
          </router-view>
          </div>
          <!--详见：https://router.vuejs.org/zh/guide/migration/index.html#router-view-%E3%80%81-keep-alive-%E5%92%8C-transition-->


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
.main_style {
  margin-top: 10px;
  margin-left: 5px;
}
.el-tabs--border-card>.el-tabs__content {
  padding: 0;
}
</style>

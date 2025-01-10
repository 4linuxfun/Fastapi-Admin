import {defineStore} from 'pinia'
import {computed, nextTick, ref} from 'vue'
import router from '@/router'

export const useTabsStore = defineStore('tabs', () => {
  const allTabs = ref([{name: '首页', path: '/'},])
  const currentTab = ref(null)
  const cacheTabs = ref([])

  const tabsList = computed(() => {
    return allTabs
  })


  // 打开新tab时执行
  function tabAdd(to) {
    const isExist = allTabs.value.some(item => {
      return item.path === to.fullPath
    })
    if (!isExist) {
      allTabs.value.push({
        name: to.name,
        path: to.fullPath
      })
      cacheTabs.value.push(to.name)
    }
    currentTab.value = to.name
  }

  function tabRemove(removeTab) {
    console.log('tab remove:', removeTab)
    for (let i = 0; i < allTabs.value.length; i++) {
      if (allTabs.value[i].name === removeTab) {
        allTabs.value.splice(i, 1)
        cacheTabs.value.splice(i, 1)
        const nextId = i === allTabs.value.length ? i - 1 : i
        currentTab.value = allTabs.value[nextId].name
        console.log(currentTab.value)
        router.push(allTabs.value[nextId].path)
      }
    }
  }

  function tabClick(selectTab) {
    console.log('tab click', selectTab)
    currentTab.value = selectTab.paneName
    console.log('current tab value:', currentTab.value)
    console.log('all tabs:', allTabs)
    allTabs.value.forEach(tab => {
      console.log(tab.name)
      if (tab.name === currentTab.value) {
        console.log('router to:', tab.path)
        router.push(tab.path)
      }
    })
  }

  return {currentTab, allTabs, cacheTabs, tabsList, tabAdd, tabRemove, tabClick}
})
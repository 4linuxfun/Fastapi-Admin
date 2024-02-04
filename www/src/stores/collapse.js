import {defineStore} from 'pinia'
import {ref} from 'vue'

export const useCollapseStore = defineStore('collapse', () => {
  const collapse = ref(false)
  return {collapse}
})
import {reactive, ref, watch, computed} from 'vue'

export default function (form, menuData, emit) {
  const selectData = reactive(form)
  const selectApis = ref([])

  if (selectData.id !== null) {
    for (const api of selectData.apis) {
      console.log(api)
      selectApis.value.push(api.id)
    }
  }

  watch(selectData, (newData) => {
    console.log('watch selectData change:' + selectData)
    selectData.apis = selectApis.value
    emit('update:form', selectData)
  })

  watch(selectApis, (newValue) => {
    console.log('selectApi watch')
    selectData.apis = selectApis.value
  })

  const menuMap = (arr) => {
    const menu = arr.filter(item => item.type !== 'btn')
    for (let item of menu) {
      if (item.children && item.children.length > 0) {
        item.children = menuMap(item.children)
      }
    }
    return menu
  }
  //cascaderMenu变量不包含menuData变量中type为btn的值，如果children属性值包含内容，则再进行遍历判断
  const cascaderMenu = computed(() => {
    let menu = menuMap(menuData)
    console.log(menu)
    return menu
  })

  return {
    selectData,
    selectApis,
    cascaderMenu
  }
}
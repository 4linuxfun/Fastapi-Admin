import {reactive, ref, watch, computed} from 'vue'

export default function (form, menuData, emit) {
  const selectData = reactive(form)

  watch(selectData, (newData) => {
    console.log('watch selectData change:' + selectData)
    emit('update:form', selectData)
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
    cascaderMenu
  }
}
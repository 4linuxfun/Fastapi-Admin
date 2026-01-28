import {createApp} from 'vue'
import App from './App.vue'
import ElementPlus from 'element-plus'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import zhCn from 'element-plus/dist/locale/zh-cn'
import 'element-plus/dist/index.css'
import router from './router'
import {createPinia} from 'pinia'
import {useStore} from './stores'
import './permission'
import 'uno.css'


const app = createApp(App)
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(ElementPlus, {locale: zhCn})
app.use(router)
app.use(createPinia())

// 权限检查方法
function checkPermission(value) {
  if (value && value instanceof Array && value.length > 0) {
    const store = useStore()
    const permissions = store.buttons
    const permissionRoles = value

    const hasPermission = permissions.some(permission => {
      return permissionRoles.includes(permission)
    })
    return hasPermission
  } else if (value && typeof value === 'string') {
    const store = useStore()
    const permissions = store.buttons
    return permissions.includes(value)
  } else {
    console.error(`need roles! Like v-permission="['admin','editor']" or v-permission="'admin'"`)
    return false
  }
}

// 全局挂载
app.config.globalProperties.$hasPermi = checkPermission
app.config.globalProperties.$hasPermission = checkPermission

app.directive('permission', {
  mounted(el, binding) {
    const { value } = binding
    if (!checkPermission(value)) {
      el.parentNode && el.parentNode.removeChild(el)
    }
  }
})
app.mount('#app')
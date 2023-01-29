import {createApp} from 'vue'
import App from './App.vue'
import ElementPlus from 'element-plus'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
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

app.directive('permission', {
  mounted(el, binding) {
    console.log('permission run')
    console.log(el, binding)
    const store = useStore()
    let permission = binding.value
    console.log('check permission:' + permission)
    let btnPermissions = store.buttons
    console.log(btnPermissions)
    if (!btnPermissions.includes(permission)) {
      el.parentNode.removeChild(el)
    }
  }
})
app.mount('#app')
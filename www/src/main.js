import { createApp } from 'vue'
import App from './App.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import router from './router'
import store from './stores'
import request from '@/utils/request'
import './permission'


const app = createApp(App)
app.config.globalProperties.$request = request
app.use(ElementPlus)
app.use(router)
app.use(store)
app.mount('#app')
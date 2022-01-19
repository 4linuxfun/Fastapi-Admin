import { createApp } from 'vue'
import App from './App.vue'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import 'element-plus/dist/index.css'
import router from './router'
import {createPinia} from 'pinia'
import request from '@/utils/request'
import './permission'

import 'xe-utils'
import VXETable from 'vxe-table'
import "vxe-table/lib/style.css"
import VXETablePluginElement from 'vxe-table-plugin-element'
import 'vxe-table-plugin-element/dist/style.css'

const app = createApp(App)
app.config.globalProperties.$request = request
app.use(ElementPlus,{ locale: zhCn})
app.use(router)
app.use(createPinia())
app.use(VXETable)
VXETable.use(VXETablePluginElement)
app.mount('#app')
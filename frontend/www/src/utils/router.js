import Layout from '@/views/Layout'
import {shallowRef} from 'vue'

// 通过服务端传回来的权限菜单列表，添加部分字段
export function makeRouter(routers) { // 遍历后台传来的路由字符串，转换为组件对象
  console.log(routers)
  let asyncRouter = routers.map(route => {
    console.log('name:' + route.name + ' path:' + route.path)
    if (route.component) {
      route.component = loadView(route.component)
    } else {
      route.component = null
    }

    if (route.children && route.children.length) {
      route.children = makeRouter(route.children)
    }
    return route
  })
  console.log('asyncrouter is:', asyncRouter) // 修改: 更改为对象输出
  return asyncRouter
}

export const loadView = (view) => { // 路由懒加载
  return () => import(`@/views/${view}`)
}

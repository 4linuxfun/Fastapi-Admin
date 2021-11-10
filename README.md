# simple_ams
简单的资产管理系统

**个人学习项目，只会对明显的bug进行修复，不会进行过多新功能的更新**

常用分支说明：
* main：主分支，所有功能都会往这里合并
* ams： 资产管理分支，后期所有资产管理的开发会先提交此分支
* admin：www管理分支，独立分支，后期可独立当简单的后端框架

## 测试环境服务启动
1. 前端启动：
```
进入www页面，执行：npm run serve
```
2. 后端启动
```
uvicorn server.main:app --reload
```


# 功能实现介绍
## 权限分配
实力有限，实现简化的权限分配功能，思路如下：
### 前端
1. 页面下的按钮需要权限管控的按钮，单独列出，再对这个按钮做权限分配
2. 在“菜单管理”中对应页面下添加“按钮”，**路径**字段需要跟到时候做权限判断时对应
3. 进入“角色管理”页面，分配对应的角色，可选择页面的按钮
    **NOTICE：**上级页面需要手动勾选，不然登录无法带出来
4. 给按钮增加**v-if**判断语法，用法如下：
    ```
     v-if="$route.meta.import === true"
    ```

### 后端
* 用户请求权限，返回子页面带meta元素，示例如下：
    ```
        [
            {
                "id": 1,
                "component": 'Layout,
                "parent_id": null,
                "url": null,
                "path": "/assets",
                "name": "资产管理",
                "type": "page",
                "enable": 1,
                "children": [
                    {
                        "id": 2,
                        "parent_id": 1,
                        "url": null,
                        "path": "add",
                        "name": "增加资产",
                        "type": "page",
                        "enable": 1
                    },
                    {
                        "id": 11,
                        "parent_id": 1,
                        "url": null,
                        "path": "system",
                        "name": "系统",
                        "type": "page",
                        "enable": 1,
                        <!-- meta元素中的import、outpu对应不同按钮的权限 -->
                        "meta": {
                            "import": true,
                            "output": true
                        }
                    }
                ]
            },
            {
                "id": 3,
                "component":  "Layout",
                "parent_id": null,
                "url": null,
                "path": "/system",
                "name": "系统管理",
                "type": "page",
                "enable": 1,
                "children": [
                    {
                        "id": 4,
                        "parent_id": 3,
                        "url": null,
                        "path": "user",
                        "name": "用户管理",
                        "type": "page",
                        "enable": 1
                    },
                    {
                        "id": 6,
                        "parent_id": 3,
                        "url": null,
                        "path": "roles",
                        "name": "角色管理",
                        "type": "page",
                        "enable": 1
                    },
                    {
                        "id": 7,
                        "parent_id": 3,
                        "url": null,
                        "path": "menus",
                        "name": "菜单管理",
                        "type": "page",
                        "enable": 1
                    }
                ]
            }
        ]
    ```
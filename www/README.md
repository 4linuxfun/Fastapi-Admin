# 自封组件介绍
## 分页查询
```javascript
// 定义查询字段，type字段定义各个查询字段的方式
/*
* type可用参数：
* 'r_like':右like模糊查询
* 'like':全模糊查询
* 'l_like':左like模糊查询
* 'eq':等于
* 'ne':不等于
* 'lt':小于
* 'le':小于等于
* 'gt':大于
* 'ge':大于等于
* */
const searchForm = {
        tags: null,
        path: null,
        method: null,
        summary: null,
        type: {
          tags: 'r_like',
          path: 'like',
          method: 'eq',
          summary: 'like',
        }
      }

      /*usePagination(url,searchForm,orderModel)
      * 
      * */
      const {
        search,
        tableData,
        currentPage,
        pageSize,
        orderModel,
        total,
        freshCurrentPage,
        handleSearch
      } = usePagination('/api/sysapis', searchForm,'desc')
```

## AutoFormDialog
### 调用
```
<auto-from-dialog v-if="addDialog.show" v-model:visible="addDialog.show" :col="2" :formItemInfo="testFormItemInfo"
		@update="handleUpdate" :title="addDialog.title">
	</auto-from-dialog>
```
### 传递属性：

* 动态表单组件  
* @description 动态表单组件
* @tutorial 无  
* @property {Boolean} visible 是否显示formdialog  
* @property {Number} col = [1|2] 显示列数
* @property {String} labelWidth = "100px" formItem label的宽度
* @property {Array} formItemInfo 表单各字段的属性  
* @event {Function} update 提交事件，返回新值对象：{prop1:value,prop2:value,prop3:value}
* @example


### formItemInfo信息
```
const formItemInfo = [{
						"type": "text", #用于判断类型
						"prop": "name", #对应绑定form的prop属性值名称，后期返回数据也是此字段名
						"value": null,  #传递的默认值
						"label": "菜单名", #formItem的label
						# 对输入字段设置对应的rules验证规则
						"rules": [{
							"required": true,
							"message": "请输入菜单名",
							"trigger": "blur"
						}],
						# formItem中对应表单组件的属性值，直接传递给相应组件
						"properties": {
							"placeholder": "请输入菜单名",
						},
					},
					{
						"type": "number",
						"prop": "age",
						"value": 11,
						"label": "年龄",
						"rules": [{
							"required": true,
							"message": "请输入年龄",
							"trigger": "blur"
						}],
						"properties": {
							"placeholder": "请输入年龄",
						},
					},
					{
						"type": "switch",
						"prop": "value",
						"value": true,
						"label": "值",
						"rules": [{
							"required": true,
							"message": "请输入值",
							"trigger": "blur"
						}],

					},
					{
						"type": "date",
						"prop": "date",
						"value": "2021-11-12",
						"label": "创建时间",
						"rules": [{
							"required": true,
							"message": "参考前端组件填写",
							"trigger": "blur"
						}],
						"properties": {
							"type": 'date',
							"placeholder": '请输入日期',
							"value-format": "YYYY-MM-DD"
						},
					},
					{
						"type": "datetime",
						"prop": "datetime",
						"value": "2021-12-12 12:12:12",
						"label": "申报时间",
						"rules": [{
							"required": true,
							"message": "参考前端组件填写",
							"trigger": "blur"
						}],
						"properties": {
							"type": 'datetime',
							"placeholder": '请输入时间',
							"value-format": "YYYY-MM-DD HH:mm:ss",
							"style": "width: 100%;"
						},
					}
				]
```

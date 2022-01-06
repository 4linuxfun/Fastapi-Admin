// 菜单管理页面，用于创建菜单关系：菜单名、菜单页面、二级菜单。。。等等
<template lang="">
	<el-row style="width:300px" :gutter="5">
		<el-col :span="18">
			<el-input v-model="search"  placeholder="搜索" clearable>
				<template #append>
					<el-button @click="getMenuInfo"><el-icon><search /></el-icon></el-button>
				</template>
			</el-input>
		</el-col>
		<el-col :span="6">
			<el-button  type="primary"  @click="handleAdd(null)">添加父菜单</el-button>
		</el-col>
	</el-row>
	<div style="padding-top:10px">
		<el-table :data="menuData" style="width: 100%; margin-bottom: 20px;" row-key="id" border default-expand-all>
			<el-table-column prop="id" label="主键" width="180" />
			<el-table-column prop="name" label="名称" width="180"/>			
			<el-table-column prop="type" label="类型" width="80">
				<template #default="scope">
					<el-tag effect="dark" v-if="(scope.row.type === 'page') && (scope.row.component === 'Layout')" type='info'>父菜单</el-tag>
					<el-tag effect="dark" v-else-if="scope.row.type === 'page' && scope.row.component !== 'Layout'" type='info'>子菜单</el-tag>
					<el-tag effect="dark" v-else type="success">按钮</el-tag>
				</template>
			</el-table-column>
			<el-table-column prop="path" label="路径" width="180" />
			<el-table-column prop="component" label="组件" width="180" />
			<el-table-column prop="api" label="API权限">
				<template #default="scope">
					<template v-if="scope.row.api != null">
						<el-tag v-for="(api,index) of splitApis(scope.row.api)" :key="index" type="success">{{api}}</el-tag>
					</template>
					
				</template>
			</el-table-column>
			<el-table-column prop="enable" label="状态" width="80">
				<template #default="scope">
					<el-tag effect="dark" :type="scope.row.enable === 1?'success':'danger'">{{scope.row.enable === 1?'启用':'禁用'}}</el-tag>
				</template>
			</el-table-column>
			<el-table-column label="操作" >
				<template #default="scope">
					<el-button type="primary" size="small" @click="handleEdit(scope.row)">编辑</el-button>
					<el-button type="danger" size="small" @click="handleDelete(scope.row.id,scope.row.name)">删除</el-button>
					<el-button v-if="scope.row.component == 'Layout'" size="small"  @click="handleAdd(scope.row.id,'page')">添加子菜单</el-button>
					<el-button v-else-if="scope.row.component !== 'Layout' && scope.row.type === 'page'"  @click="handleAdd(scope.row.id,'btn')">添加按钮</el-button>
				</template>
			</el-table-column>>
		</el-table>
		
	</div>
	<div v-if="dialogVisible">
		<menu-dialog :data="selectData" v-model:visible="dialogVisible"></menu-dialog>
	</div>
	
</template>
<script>
	import { Search } from '@element-plus/icons-vue'
	import {
		DeleteMenu,
		GetAllMenus
	} from '@/api/menus'
	import MenuDialog from './MenuDialog'
	export default {
		components: {
			Search,
			'menu-dialog':MenuDialog,
		},
		data() {
			return {
				search:null,
				dialogVisible: false,
				menuInfo: {
					name: '',
					status: ''
				},
				// 表格数据
				menuData: [],
				// 点击编辑菜单时选择的数据
				selectData: '',
			}

		},
		created() {
			console.log('start to get all menu list')
			this.getMenuInfo()
		},
		watch: {
			dialogVisible(newValue){
				if(newValue === false){
					this.getMenuInfo()
				}
				
			},
		},
		methods: {
			splitApis(apis){
				console.log('split')
				console.log(apis)
				return apis.split(',')
			},
			onSubmit() {
				console.log('submit!')
			},
			handleEdit(row) {
				this.dialogVisible = true
				this.selectData = Object.assign({}, row)
			},
			handleDelete(id,name){
				this.$confirm('是否删除菜单：'+id + ': ' +name,'删除菜单',{
					type:'warning'
				}).then(()=>{
					DeleteMenu(id)
					this.getMenuInfo()
				}).catch()
			},
			handleAdd(id,type=null){
				this.dialogVisible = true
				if(id===null && type === null){
					console.log('添加父级菜单')
					this.selectData = {
						id:null,
						parent_id:null,
						name:'',
						path:'',
						component:"Layout",
						enable:'',
						type:'page'
						
					}
				}else if(id!== null && type === 'page'){
					this.selectData = {
						id:null,
						parent_id:id,
						name:'',
						path:'',
						component:'',
						enable:'',
						type:'page'
						
					}
				} else if (id !== null && type === 'btn'){
					this.selectData = {
						id:null,
						parent_id:id,
						name:'',
						path:'',
						component:'',
						enable:'',
						type:'button'
					}	
				}
			},
			getMenuInfo() {
				console.log('get menu info')
				GetAllMenus(this.search).then(response => {
					console.log(response)
					this.menuData = response
				}).catch(error => {
					this.$notify({
						title:"错误",
						message:error,
						type:"error"
					})
				})
			},
			
		},
	}
</script>
<style lang="">

</style>

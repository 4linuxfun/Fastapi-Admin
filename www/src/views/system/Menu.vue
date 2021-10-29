// 菜单管理页面，用于创建菜单关系：菜单名、菜单页面、二级菜单。。。等等
<template lang="">
	<div>
		<el-button>添加父菜单</el-button>
		<el-table :data="menuData" style="width: 100%; margin-bottom: 20px;" row-key="id" border default-expand-all>
			<el-table-column prop="id" label="主键" width="180" />
			<el-table-column prop="name" label="菜单名称" width="180" />
			<el-table-column prop="path" label="路径" width="180" />
			<el-table-column prop="component" label="组件" width="180" />
			<el-table-column prop="enable" label="状态" width="80">
				<template #default="scope">
					<el-tag effect="dark" :type="scope.row.enable === 1?'success':'danger'">{{scope.row.enable === 1?'启用':'禁用'}}</el-tag>
				</template>
			</el-table-column>
			<el-table-column label="操作" >
				<template #default="scope">
					<el-button type="primary" size="small" @click="handleEdit(scope.row)">编辑</el-button>
					<el-button type="danger" size="small" @click="handleDelete(scope.row.id,scope.row.name)">删除</el-button>
					<el-button v-if="scope.row.component == 'Layout'" size="small"  @click="handleAdd(scope.row.id)">添加子菜单</el-button>
				</template>
			</el-table-column>>
		</el-table>
		
	</div>
	<div v-if="dialogVisible">
		<menu-dialog v-model:data="selectData" v-model:visible="dialogVisible" @update:data="updateMenu"></menu-dialog>
	</div>
	
</template>
<script>
	import {
		requestUpdateMenu,
		requestDelMenu,
		requestGetAllMenu
	} from '@/api/menu'
	import MenuDialog from '@/components/MenuDialog'
	export default {
		components: {
			'menu-dialog':MenuDialog,
		},
		data() {
			return {
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
		methods: {
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
					requestDelMenu(id)
					this.getMenuInfo()
				}).catch()
			},
			handleAdd(id){
				this.dialogVisible = true
				this.selectData = {
					id:null,
					parent_id:id,
					name:'',
					path:'',
					component:'',
					enable:'',
					type:'page'
					
				}
			},
			updateMenu(data) {
				console.log(data)
				this.dialogVisible = false
				requestUpdateMenu(data)
				this.getMenuInfo()
			},
			
			getMenuInfo() {
				console.log('get menu info')
				requestGetAllMenu().then(response => {
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

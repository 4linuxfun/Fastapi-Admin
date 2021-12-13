<template>
		<el-dialog :model-value="visible" title="角色编辑页面" width="50%" @close="$emit('update:visible',false)" @opened="getInfo" destroy-on-close>
			<el-form :model="selectData" label-width="80px">
				<el-form-item label="角色名称">
					<el-input v-model="selectData.name"></el-input>
				</el-form-item>
				<el-form-item label="角色描述">
					<el-input v-model="selectData.description"></el-input>
				</el-form-item>
				<el-form-item label="状态">
					<el-radio-group v-model="selectData.enable">
						<el-radio :label="0" size="medium">禁用</el-radio>
						<el-radio :label="1" size="medium">启用</el-radio>
					</el-radio-group>
				</el-form-item>
				<el-form-item label="菜单" style="border-style: solid;">
					<el-tree ref="tree" :data="menus" :props="defaultProps" show-checkbox node-key="id" :default-checked-keys="enables"></el-tree>
				</el-form-item>
				<el-form-item label="资产" style="border-style: solid;">
					<el-transfer v-model="categoryEnables" :props="{key:'id',label:'name'}" :data="category" :titles="['无权限','有权限']"></el-transfer>
				</el-form-item>
				<el-form-item>
					<el-button @click="$emit('update:visible',false)">取消</el-button>
					<el-button v-if="selectData.id" type="primary" @click="handleUpdate">更新</el-button>
					<el-button v-else type="primary" @click="handleUpdate">添加</el-button>
				</el-form-item>
			</el-form>
		</el-dialog>
	
</template>

<script>
	import {GetRoleEnableMenus} from '@/api/index'
	export default {
		props:['role','visible'],
		emits:['update:role','update:visible'],
		data() {
			return {
				selectData: this.role,
				menus: '',
				defaultProps:{
					children:'children',
					label:'name'
				},
				// 拥有权限的菜单ID列表
				enables:'',
				category: [],
				categoryEnables:[]
			}
		},
		mounted() {
			this.$request({
				url:'/api/role/category',
				method:'get',
				params:{
					id: this.role.id
				}
			}).then((response)=>{
				console.log(response)
				this.category = response.category
				this.categoryEnables = response.enable
			})
		},
		methods: {
			// updateMenu() {
			// 	this.$emit('update',this.selectData)
			// 	this.$emit('cancel')
			// },
			getInfo(){
				console.log('请求menus信息')
				GetRoleEnableMenus(this.role.id).then((response)=>{
					console.log(response)
					this.menus = response.menus
					this.enables = response.enable
				})
				console.log('请求category信息')
				
				
			},
			handleUpdate(){
				let checkedKeys = this.$refs.tree.getCheckedKeys().concat(this.$refs.tree.getHalfCheckedKeys())
				console.log(checkedKeys)
				this.$emit('update:role',this.selectData,checkedKeys,this.categoryEnables)
				this.$emit('update:visible',false)
			}
			
		},
	}
</script>

<style>
</style>

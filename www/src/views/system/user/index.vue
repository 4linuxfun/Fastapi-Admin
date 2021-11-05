<template lang="">
	<div>
		<el-table :data="userInfo" border style="width: 100%">
			<el-table-column prop="id" label="ID" width="180">
			</el-table-column>
			<el-table-column prop="name" label="用户名" width="180">
			</el-table-column>
			<el-table-column prop="enable" label="状态">
				<template #default="scope">
					<el-tag effect="dark" :type="scope.row.enable === 1?'success':'danger'">{{scope.row.enable === 1?'启用':'禁用'}}</el-tag>
				</template>
			</el-table-column>
			<el-table-column label="操作">
				<template #default="scope">
					<template v-if="scope.row.name=='admin'">
						<el-button  type="primary" size="small" @click="handleAdd">添加新用户</el-button>
					</template>
					<template v-else>
						<el-button type="primary" size="small" @click="handleEdit(scope.row)">编辑</el-button>
						<el-button type="danger" size="small" @click="handleDel(scope.row.id,scope.row.name)">删除</el-button>
					</template>
					
				</template>
			</el-table-column>
		</el-table>
	</div>
	<div v-if="dialogVisible">
		<user-dialog v-model:user='selectUser' v-model:visible='dialogVisible' @update:user="handleUpdate"></user-dialog>
	</div>
</template>
<script>
	import UserDialog from './UserDialog.vue'
	import {requestUsers,requestUpdateUser,requestDelUser} from '@/api/login'
	export default {
		components:{
			'user-dialog':UserDialog,
		},
		created() {
			this.getUsers()
		},
		data() {
			return {
				dialogVisible:false,
				userInfo: '',
				selectUser:'',
			};
		},
		methods: {
			getUsers() {
				requestUsers().then((response)=>{
					this.userInfo = response
				})
				
			},
			handleEdit(user){
				this.dialogVisible=true
				this.selectUser = Object.assign({}, user)
			},
			handleUpdate(user,roleList){
				requestUpdateUser(user,roleList).then(()=>{
					this.$notify({
						title:'success',
						message:"用户更新成功",
						type:'success'
					})
					this.getUsers()
				})
			},
			handleAdd(){
				this.selectUser = {
					id:null,
					name:'',
					password:'',
					enable:'',
				}
				this.dialogVisible=true
			},
			handleDel(userId,userName){
				this.$confirm("是否确定要删除用户："+userName, "Warnning").then(()=>{
					requestDelUser(userId).then(()=>{
						this.$notify({
							title:'success',
							message:"角色删除成功",
							type:'success'
						})
						this.getUsers()
					})
				}).catch(()=>{
					this.$notify({
						title:'success',
						message:"取消删除操作",
						type:'success'
					})
				})
			}
		},
	};
</script>

<style>
</style>

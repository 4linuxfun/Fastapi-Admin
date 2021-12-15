<template lang="">
	<el-row style="width:300px" :gutter="5">
		<el-col :span="18">
			<el-input v-model="search"  placeholder="搜索" clearable>
				<template #append>
					<el-button @click="getUsers"><el-icon><search /></el-icon></el-button>
				</template>
			</el-input>
		</el-col>
		<el-col :span="6">
			<el-button  type="primary"  @click="handleAdd">添加新用户</el-button>
		</el-col>
	</el-row>

	<div style="padding-top:10px">
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
					<el-button type="primary" size="small" @click="handleEdit(scope.row)">编辑</el-button>
					<el-button type="danger" size="small" @click="handleDel(scope.row.id,scope.row.name)">删除</el-button>
				</template>
					
				
			</el-table-column>
		</el-table>
	</div>
	<div v-if="dialogVisible">
		<user-dialog v-model:user='selectUser' v-model:visible='dialogVisible' @update:user="handleUpdate"></user-dialog>
	</div>
</template>
<script>
import { Search } from '@element-plus/icons-vue'
import UserDialog from './UserDialog.vue'
import { GetUsers, PutNewUser, PostAddUser, DeleteUser } from '@/api/users'
export default {
	components: {
		Search,
		'user-dialog': UserDialog,
	},
	created() {
		this.getUsers()
	},
	data() {
		return {
			search:null,
			dialogVisible: false,
			userInfo: '',
			selectUser: '',
		};
	},
	methods: {
		getUsers() {
			GetUsers(this.search).then((response) => {
				this.userInfo = response
			})

		},
		handleEdit(user) {
			this.dialogVisible = true
			this.selectUser = Object.assign({}, user)
		},
		handleUpdate(user, roleList) {
			if (user.id === null) {
				PostAddUser(user, roleList).then(() => {
					this.$notify({
						title: 'success',
						message: "用户新建成功",
						type: 'success'
					})
					this.getUsers()
				})
			} else {
				PutNewUser(user, roleList).then(() => {
					this.$notify({
						title: 'success',
						message: "用户更新成功",
						type: 'success'
					})
					this.getUsers()
				})
			}

		},
		handleAdd() {
			this.selectUser = {
				id: null,
				name: '',
				password: '',
				enable: '',
			}
			this.dialogVisible = true
		},
		handleDel(userId, userName) {
			if (userName === 'admin') {
				this.$message({
					message: "admin用户无法删除",
					type: 'warning'
				})
				return false
			}
			this.$confirm("是否确定要删除用户：" + userName, "Warnning").then(() => {
				DeleteUser(userId).then(() => {
					this.$notify({
						title: 'success',
						message: "角色删除成功",
						type: 'success'
					})
					this.getUsers()
				})
			}).catch(() => {
				this.$notify({
					title: 'success',
					message: "取消删除操作",
					type: 'success'
				})
			})
		}
	},
};
</script>

<style>
</style>

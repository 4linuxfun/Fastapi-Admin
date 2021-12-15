<template lang="">
	<!-- 角色管理页面 -->
	<el-row style="width:300px" :gutter="5">
		<el-col :span="18">
			<el-input v-model="search"  placeholder="搜索" clearable>
				<template #append>
					<el-button @click="getRoles"><el-icon><search /></el-icon></el-button>
				</template>
			</el-input>
		</el-col>
		<el-col :span="6">
			<el-button  type="primary"  @click="addRole">添加新角色</el-button>
		</el-col>
	</el-row>

	<div style="padding-top:10px">
		<el-table :data="roles" border >
			<el-table-column label="角色ID" prop="id"></el-table-column>
			<el-table-column label="角色名称" prop="name"></el-table-column>
			<el-table-column label="描述" prop="description"></el-table-column>
			<el-table-column label="状态">
				<template #default="scope">
					<el-tag effect="dark" :type="scope.row.enable === 1?'success':'danger'">{{scope.row.enable === 1?'启用':'禁用'}}</el-tag>
				</template>
			</el-table-column>
			<el-table-column label="操作">
				<template #default="scope">
					<el-button type="primary" size="small" @click="handleEdit(scope.row)">编辑权限</el-button>
					<el-button type="danger" size="small" @click="handleDel(scope.row.id,scope.row.name)">删除</el-button>
				</template>
			</el-table-column>
		</el-table>
	</div>
    
	<div v-if="dialogVisible">
		<role-dialog v-model:role='selectRole' v-model:visible='dialogVisible' @update:role="handleUpdate"></role-dialog>
	</div>
	
</template>
<script>
import { Search } from '@element-plus/icons-vue'
import { GetRoles, PutRoles, DeleteRole } from '@/api/roles'
import RoleDialog from './RoleDialog.vue'
export default {
	components: {
		Search,
		'role-dialog': RoleDialog
	},
	created() {
		this.getRoles()
	},
	data() {
		return {
			search: null,
			roles: '',
			dialogVisible: false,
			selectRole: '',
			addDialog: false
		}
	},
	methods: {
		// 更新数据后，可以执行此调用，重新获取新的数据，达到刷新效果
		getRoles() {
			GetRoles(this.search).then((response) => {
				this.roles = response
			})

		},
		handleEdit(role) {
			console.log(role)
			this.selectRole = Object.assign({}, role)
			console.log(this.selectRole)
			this.dialogVisible = true
		},
		handleUpdate(role, menuList, category) {
			console.log(role, menuList, category)
			PutRoles(role, menuList, category).then(() => {
				this.$notify({
					title: 'success',
					message: "菜单权限更新成功",
					type: 'success'
				})
				this.getRoles()
			})
		},
		handleDel(roleId, roleName) {
			if (roleName === 'admin') {
				this.$message({
					message: "admin角色无法删除",
					type: "warning"
				})
				return false
			}
			this.$confirm("是否确定要删除角色：" + roleName, "Warnning").then(() => {
				DeleteRole(roleId).then(() => {
					this.$notify({
						title: 'success',
						message: "角色删除成功",
						type: 'success'
					})
					this.getRoles()
				})
			}).catch(() => {
				this.$notify({
					title: 'success',
					message: "取消删除操作",
					type: 'success'
				})
			})

		},
		addRole() {
			this.selectRole = {
				id: null,
				name: '',
				description: '',
				enable: ''
			}
			console.log(this.selectRole)
			this.dialogVisible = true
		}
	},

}
</script>
<style lang="">
    
</style>
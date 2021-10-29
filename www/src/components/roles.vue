<template lang="">
	<!-- 角色管理页面 -->
    <el-table :data="roles" border>
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
				<el-button type="primary" size="small" @click="handleEdit(scope.row.id)">编辑权限</el-button>
				<el-button type="danger" size="small">删除</el-button>
			</template>
		</el-table-column>
	</el-table>
</template>
<script>
	import {requestRoles,requestRoleInfo} from '@/api/roles'
export default {
	created() {
		this.getRoles()
	},
	data() {
		return {
			roles:'',
			roleInfo:''
		}
	},
	methods: {
		getRoles() {
			this.roles =await requestRoles()
		},
		handleEdit(roleId){
			roleInfo = await requestRoleInfo(roleId)
		}
	},
	
}
</script>
<style lang="">
    
</style>
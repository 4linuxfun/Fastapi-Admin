<template>
	<el-dialog :model-value="visible" title="用户编辑页面" width="30%" @close="$emit('update:visible',false)"
		@opened="getRoles(selectData.id)" destroy-on-close>
		<el-form :model="selectData" label-width="80px">
			<el-form-item label="用户名称">
				<el-input v-model="selectData.name"></el-input>
			</el-form-item>
			<el-form-item label="密码">
				<el-input v-model="password" placeholder="请输入新密码" :show-password="true"></el-input>
			</el-form-item>
			<el-form-item label="状态">
				<el-radio-group v-model="selectData.enable">
					<el-radio :label="0" size="medium">禁用</el-radio>
					<el-radio :label="1" size="medium">启用</el-radio>
				</el-radio-group>
			</el-form-item>
			<el-form-item label="角色">
				<el-checkbox-group v-model="enableRoleList">
					<el-checkbox v-for="role in roleList" :label="role.name" :key="role.id" :disabled="role.enable?false:true"/>
				</el-checkbox-group>
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
	import {
		GetUserRoles
	} from '@/api/users'
	import md5 from 'js-md5'
	export default {
		props: ['user', 'visible'],
		emits: ['update:user', 'update:visible'],
		data() {
			return {
				selectData: this.user,
				// 所有权限列表
				roleList: [],
				// 拥有权限的列表
				enableRoleList: [],
				password: ''
			}
		},
		methods: {
			// updateMenu() {
			// 	this.$emit('update',this.selectData)
			// 	this.$emit('cancel')
			// },
			getRoles(userId) {
				GetUserRoles(userId).then((response) => {
					this.roleList = response.roles
					this.enableRoleList = response.enable
				})



			},
			handleUpdate() {
				if (this.password) {
					this.selectData.password = md5(this.password)
				}
				this.$emit('update:user', this.selectData, this.enableRoleList)
				this.$emit('update:visible', false)
			}

		},
	}
</script>

<style>
</style>

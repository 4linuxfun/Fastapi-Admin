<template lang="">
	<el-row style="width:300px" :gutter="5">
		<el-col :span="18">
			<el-input v-model="search" placeholder="搜索" clearable>
				<template #append>
					<el-button @click="handleSearch">
						<el-icon>
							<search />
						</el-icon>
					</el-button>
				</template>
			</el-input>
		</el-col>
		<el-col :span="6">
			<el-button type="primary" @click="handleAdd">添加新用户</el-button>
		</el-col>
	</el-row>

	<div style="padding-top:10px">
		<vxe-table :data="tableData" align="center" border="full" size="medium" :row-config="{isHover:true}">
			<vxe-column type="seq" width="60"></vxe-column>
			<vxe-column field="name" title="用户名"></vxe-column>
			<vxe-column field="enable" title="状态">
				<template #default="scope">
					<el-tag effect="dark" :type="scope.row.enable === 1?'success':'danger'">
						{{scope.row.enable === 1?'启用':'禁用'}}
					</el-tag>
				</template>
			</vxe-column>
			<vxe-column title="操作">
				<template #default="scope">
					<el-button type="primary" size="small" @click="handleEdit(scope.row)">编辑</el-button>
					<el-button type="danger" size="small" @click="handleDel(scope.row.id,scope.row.name)">删除</el-button>
				</template>
			</vxe-column>
		</vxe-table>
		<!-- <el-pagination v-model:current-page="currentPage" background :page-sizes="[10,20,50,100]"
			v-model:page-size="pageSize" layout="total,sizes,prev,pager,next,jumper" :total="total" prev-text="上一页"
			next-text="下一页"></el-pagination> -->
		<vxe-pager v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total" align="left"
			:layouts="['PrevJump', 'PrevPage', 'JumpNumber', 'NextPage', 'NextJump', 'Sizes', 'FullJump', 'Total']">
		</vxe-pager>
	</div>
	<div v-if="dialogVisible">
		<user-dialog v-model:user='selectUser' v-model:visible='dialogVisible' @update:user="handleUpdate">
		</user-dialog>
	</div>
</template>
<script>
	import {
		ref
	} from 'vue'
	import {
		Search
	} from '@element-plus/icons-vue'
	import UserDialog from './UserDialog.vue'
	import usePagination from '@/composables/usePagination'
	import {
		GetUsers,
		PutNewUser,
		PostAddUser,
		DeleteUser
	} from '@/api/users'
	export default {
		components: {
			Search,
			'user-dialog': UserDialog,
		},
		setup() {
			const dialogVisible = ref(false)
			const selectUser = ref(null)


			// 首次打开页面先进行初始化

			const {
				search,
				tableData,
				currentPage,
				pageSize,
				total,
				firstId,
				lastId,
				freshCurrentPage,
				handleSearch
			} = usePagination(GetUsers)
			return {
				search,
				dialogVisible,
				tableData,
				selectUser,
				pageSize,
				currentPage,
				total,
				lastId,
				firstId,
				freshCurrentPage,
				handleSearch
			}
		},
		methods: {

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
						this.freshCurrentPage()
					})
				} else {
					PutNewUser(user, roleList).then(() => {
						this.$notify({
							title: 'success',
							message: "用户更新成功",
							type: 'success'
						})
						this.freshCurrentPage()
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
						this.freshCurrentPage()
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

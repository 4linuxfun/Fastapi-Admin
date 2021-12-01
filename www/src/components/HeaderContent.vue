<template lang="">
	<div>
		<el-row justify="end">
			<el-col :span="4">
				<div style="padding-top: 10px;">
					<el-dropdown trigger="click" @command="handleCommand">
						<el-avatar shape="circle" :size="50">Admin</el-avatar>
						<template #dropdown>
							<el-dropdown-menu>
								<el-dropdown-item>个人中心</el-dropdown-item>
								<el-dropdown-item command="logout">退出</el-dropdown-item>
							</el-dropdown-menu>
						</template>
					</el-dropdown>
				</div>
			</el-col>
		</el-row>
	</div>
</template>
<script>
	import {
		ElMessage,
		ElMessageBox
	} from 'element-plus';

	export default {
		name: "HeaderContent",
		methods: {
			handleCommand(command){
				if(command==='logout'){
					this.logOut()
				}
			},
			logOut() {
				console.log("click logout button");
				ElMessageBox.confirm('确定退出系统吗？', '提示', {
					confirmButtonText: '是',
					cancelButtonText: '否',
					type: 'warning'
				}).then(() => {
					this.$store.dispatch('logOut');
					this.$router.push('/login');
					ElMessage({
						type: 'success',
						message: '退出成功！'
					});
				}).catch(() => {
					ElMessage({
						type: 'info',
						message: '取消退出'
					});
				});

			},
		},
	};
</script>
<style lang="">
</style>

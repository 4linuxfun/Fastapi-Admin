<template>
	<!-- 详细信息、单数据更新页面 -->
	<el-dialog :model-value="visible" title="数据详情" width="70%" @close="$emit('update:visible',false)"
		destroy-on-close>
		<el-descriptions :border="true">
			<el-descriptions-item label="资产类型">{{data.category}}</el-descriptions-item>
			<el-descriptions-item label="管理员">{{data.manager}}</el-descriptions-item>
			<el-descriptions-item label="区域">{{data.area}}</el-descriptions-item>
			<el-descriptions-item label="使用人">{{data.user}}</el-descriptions-item>
			<el-descriptions-item v-for="(value,name) in data.info" :key="name"  :label="name">{{value}}</el-descriptions-item>
		</el-descriptions>
	</el-dialog>

</template>

<script>
	export default {
		props: ['data', 'visible',],
		emits:['update:visible']
	}
</script>

<style>
</style>

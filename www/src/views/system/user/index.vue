// 用户管理页面，需要功能：
// 1. 用户的查看
// 2. 用户的增加、禁用
<template lang="">
	<div style="float: left">
		<el-form :inline="true" :model="searchForm">
			<el-form-item label="部门">
				<el-input v-model="searchForm.depart"></el-input>
			</el-form-item>
			<el-form-item label="姓名">
				<el-input v-model="searchForm.name"></el-input>
			</el-form-item>
			<el-form-item>
				<el-button type="primary" @click="onSubmit">查询</el-button>
			</el-form-item>
		</el-form>
	</div>
	<div>
		<el-table :data="tableData" border style="width: 100%">
			<el-table-column prop="id" label="ID" width="180">
			</el-table-column>
			<el-table-column prop="name" label="姓名" width="180">
			</el-table-column>
			<el-table-column prop="role" label="角色">
			</el-table-column>
		</el-table>
	</div>
	<div>
		<el-pagination background layout="prev, pager, next" :total="1000">
		</el-pagination>
	</div>
</template>
<script>
	export default {
		data() {
			return {
				searchForm: {
					depart: "",
					name: "",
				},
				tableData: '',
			};
		},
		methods: {
			onSubmit() {
				console.log("submit");
			},
		},
	};
</script>

<style>
</style>

<template>
	<!-- 导入模板Dialog -->
	<el-dialog :model-value="visible" :title="title" width="30%" @close="$emit('update:visible',false)" destroy-on-close>
		<el-form :model="formData" :disabled="disabled" label-width="100px">
			<el-form-item label="资产类型">
				<el-input v-model="formData.category" disabled></el-input>
			</el-form-item>
			<el-form-item label="管理员">
				<el-input v-model="formData.manager"></el-input>
			</el-form-item>
			<el-form-item label="区域">
				<el-input v-model="formData.area"></el-input>
			</el-form-item>
			<el-form-item label="使用人">
				<el-input v-model="formData.user"></el-input>
			</el-form-item>
			<template v-for="(value,name) in formData.info" :key="name">
				<el-form-item :label="name">
					<el-input v-model="formData.info[name]"></el-input>
				</el-form-item>
			</template>
			<el-form-item v-if="disabled == false">
				<el-button type="danger">取消</el-button>
				<el-button type="primary" @click="$emit('upload',formData),$emit('update:visible',false)">更新</el-button>
			</el-form-item>
		</el-form>

	</el-dialog>
</template>

<script>

	export default {
		props: ['data', 'visible',"title","disabled"],
		emits: ['update:data', 'upload', 'update:visible'],
		data() {
			return {
				formData: this.data,
			}
		},
		methods: {
		},
	}
</script>

<style>
</style>

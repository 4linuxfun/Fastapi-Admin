<template>
	<!-- 详细信息、单数据更新页面 -->
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
				<el-form-item :label="fieldMap[name]">
					<el-input v-model="formData.info[name]"></el-input>
				</el-form-item>
			</template>
			<el-form-item v-if="disabled == false">
				<el-button type="danger" @click="$emit('update:visible',false)">取消</el-button>
				<el-button type="primary" @click="updateFields(formData)">更新</el-button>
			</el-form-item>
		</el-form>
	
	</el-dialog>
	
</template>

<script>
	import request from '@/utils/request'
	export default {
		props: ['data','fieldMap','visible',"title","disabled"],
		emits: ['update:data', 'reload', 'update:visible'],
		// created() {
		// 	console.log(this.data)
		// },
		data() {
			return {
				formData: this.data,
			}
		},
		methods: {
			updateFields(fields){
				console.log(fields)
				this.$emit('update:visible',false)
				this.$emit('reload')
				request({
					url:"/api/assets/update_category_detail",
					method:"post",
					data:fields
				}).then(()=>{
					console.log('更新成功')
				})
			},
		},
	}
</script>

<style>
</style>

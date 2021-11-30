<template>
	<!-- 详细信息、单数据更新页面 -->
	<el-dialog :model-value="visible" title="数据更新" width="30%" @close="$emit('update:visible',false)" destroy-on-close>
		<el-form :model="formData" label-width="100px">
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
					<input-plus v-model:data="formData.info[name]" :type="fieldsType[name]"></input-plus>
				</el-form-item>
			</template>
			<el-form-item>
				<el-button type="danger" @click="$emit('update:visible',false)">取消</el-button>
				<el-button type="primary" @click="updateFields(formData)">更新</el-button>
			</el-form-item>
		</el-form>
	
	</el-dialog>
	
</template>

<script>
	import request from '@/utils/request'
	import InputPlus from '@/components/InputPlus'
	export default {
		props: ['data','visible','fieldsInfo'],
		emits: ['update:data', 'reload', 'update:visible'],
		components: {
			'input-plus': InputPlus,
		},
		// created() {
		// 	console.log(this.data)
		// },
		mounted() {
			for(let field of this.fieldsInfo){
				this.fieldsType[field.name] = field.type
			}
			console.log(this.fieldsType)
		},
		data() {
			return {
				formData: this.data,
				fieldsType: {}
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

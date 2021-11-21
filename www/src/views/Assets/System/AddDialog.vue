<template>
	<!-- 单条数据录入页面 -->
	<el-dialog :model-value="visible" :title="title" width="30%" @close="$emit('update:visible',false)" destroy-on-close>
		<el-form :model="formData" label-width="100px">
			<el-form-item label="资产类型">
				<category-select style="width: 100%;" v-model:category="formData.category" placeholder="资产类型" @handleSelect="handleSelect"></category-select>
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
				<!-- <span>{{fields[name][type]}}</span> -->
				<el-form-item :label="name">
					<el-input v-if="fields[name].type=='text'" v-model="formData.info[name]" placeholder="请输入"></el-input>
					<el-input-number v-else-if="fields[name].type=='number'" v-model="formData.info[name]" placeholder="请输入" style="width: 100%;"></el-input-number>
					<el-date-picker v-else-if="fields[name].type=='date'" :type="fields[name].type" v-model="formData.info[name]" placeholder="选择日期" 
						value-format="YYYY-MM-DD"	style="width: 100%;"></el-date-picker>
					<el-date-picker v-else-if="fields[name].type=='datetime'" :type="fields[name].type" v-model="formData.info[name]" placeholder="选择日期"
						value-format="YYYY-MM-DD HH:mm:ss"	style="width: 100%;"></el-date-picker>
				</el-form-item>
			</template>

			<el-form-item>
				<el-button type="danger" @click="$emit('update:visible',false)">取消</el-button>
				<el-button type="primary" @click="handleAdd">添加</el-button>
			</el-form-item>
		</el-form>
	
	</el-dialog>
	
</template>

<script>
	import request from '@/utils/request'
	import CategorySelect from '@/components/CategorySelect'
	export default{
		props: ['visible',"title"],
		emits: ['reload', 'update:visible'],
		components: {
			'category-select': CategorySelect,
		},
		data() {
			return {
				formData: {
					category: null,
					manager: null,
					area: null,
					user: null,
					info: {},
				},
				fields:{},
			}
		},
		computed: {
			category() {
				return this.formData.category 
			},
		},
		watch: {
			category(newValue, oldValue) {
				console.log(newValue + ' '+ oldValue)
			}
		},
		methods: {
			handleSelect(item) {
				this.formData.info = {}
				request({
					url: '/api/assets/category_field/' + item.id,
					method: 'get',
				}).then((fieldList) => {
					for (let field of fieldList) {
						let fieldName = field.name
						this.fields[fieldName] = field
						this.formData.info[fieldName] = ''
					}
				})
				console.log(this.fields)
			},
			handleAdd(){
				console.log(this.formData)
				this.$emit('update:visible',false)
				request({
					url:'/api/assets/add',
					method:'post',
					data:this.formData
				}).then(()=>{
					this.$message({
						message:'资产添加成功',
						type:'success'
					})
				}).catch(()=>{
					this.$message({
						message:'资产添加失败',
						type:'warning'
					})
				})
			},
		},
	}
</script>

<style>
</style>

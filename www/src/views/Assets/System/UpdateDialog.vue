<template>
	<!-- 详细信息、单数据更新页面 -->
	<el-dialog :model-value="visible" title="数据更新" width="50%" @close="$emit('update:visible',false)" destroy-on-close>
		<el-form :model="formData" label-width="100px">
			<el-row>
				<el-col :span="12">
					<el-form-item label="资产类型">
						<el-input v-model="formData.category" disabled></el-input>
					</el-form-item>
					<el-form-item label="管理员">
						<el-input v-model="formData.manager"></el-input>
					</el-form-item>
				</el-col>
				<el-col :span="12">
					<el-form-item label="区域">
						<el-input v-model="formData.area"></el-input>
					</el-form-item>
					<el-form-item label="使用人">
						<el-input v-model="formData.user"></el-input>
					</el-form-item>
				</el-col>
			</el-row>
			<template v-for="(name,index) in fieldList" :key="index">
				<el-row v-if="index%2==0">
					<el-col :span="12">
						<el-form-item :label="fieldList[index]">
							<input-plus v-model:data="formData.info[name]" :type="fieldsType[name]"></input-plus>
						</el-form-item>
					</el-col>
					<el-col :span="12">
						<el-form-item :label="fieldList[index+1]">
							<input-plus v-model:data="formData.info[fieldList[index+1]]"
								:type="fieldsType[fieldList[index+1]]"></input-plus>
						</el-form-item>
					</el-col>
				</el-row>
			</template>
			<el-form-item>
				<el-button type="danger" @click="$emit('update:visible',false)">取消</el-button>
				<el-button type="primary" @click="updateFields(formData)">更新</el-button>
			</el-form-item>
		</el-form>

	</el-dialog>

</template>

<script>
	import {PutAssets} from '@/api/assets'
	import InputPlus from '@/components/InputPlus'
	export default {
		props: ['data', 'visible', 'fieldsInfo'],
		emits: ['update:data', 'reload', 'update:visible'],
		components: {
			'input-plus': InputPlus,
		},
		// created() {
		// 	console.log(this.data)
		// },
		mounted() {
			for (let field of this.fieldsInfo) {
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
		computed: {
			fieldList() {
				console.log('fields info')
				console.log(this.fieldsInfo)
				let fields = []
				for (let field of this.fieldsInfo) {
					console.log(field)
					fields.push(field.name)
				}
				console.log(fields)
				return fields
			}
		},
		methods: {
			updateFields(fields) {
				console.log(fields)
				this.$emit('update:visible', false)
				this.$emit('reload')
				PutAssets(fields).then(() => {
					console.log('更新成功')
				})
			},
		},
	}
</script>

<style>
</style>

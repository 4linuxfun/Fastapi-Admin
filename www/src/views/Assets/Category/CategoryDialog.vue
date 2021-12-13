<template>
	<el-dialog
		:model-value="visible"
		title="资产添加"
		width="70%"
		@close="$emit('update:visible', false)"
		destroy-on-close
	>
		<el-form v-model="categoryInfo" label-width="80px">
			<el-row>
				<el-col :span="8">
					<el-form-item label="资产类型">
						<el-input v-model="categoryInfo.category.name" placeholder="必填"></el-input>
					</el-form-item>
				</el-col>
				<el-col :span="8">
					<el-form-item label="别名">
						<el-input v-model="categoryInfo.category.alias" placeholder="可选"></el-input>
					</el-form-item>
				</el-col>
			</el-row>
			<el-form-item label="描述">
				<el-input v-model="categoryInfo.category.desc" placeholder="可选"></el-input>
			</el-form-item>
			<template v-for="field in categoryInfo.fields" :key="field.id">
				<el-row>
					<el-col :span="4">
						<el-form-item label="字段">
							<el-input v-model="field.name"></el-input>
						</el-form-item>
					</el-col>
					<el-col :span="8">
						<el-form-item label-width="0">
							<el-radio-group v-model="field.type">
								<el-radio-button label="text">字符串</el-radio-button>
								<el-radio-button label="number">数值</el-radio-button>
								<el-radio-button label="date">日期</el-radio-button>
								<el-radio-button label="datetime">日期时间</el-radio-button>
							</el-radio-group>
						</el-form-item>
					</el-col>
					<el-col :span="2">
						<el-form-item label-width="0">
							必填
							<el-switch
								v-model="field.need"
								inline-prompt
								:active-value="1"
								:inactive-value="0"
								@change="switchChange"
							/>
						</el-form-item>
					</el-col>
					<el-col :span="2">
						<el-form-item label-width="0">
							多值
							<el-switch v-model="field.multi" inline-prompt :active-value="1" :inactive-value="0" />
						</el-form-item>
					</el-col>
					<el-col :span="2">
						<el-form-item label-width="0">
							显示
							<el-switch
								v-model="field.show"
								inline-prompt
								:active-value="1"
								:inactive-value="0"
								@change="switchChange"
							/>
						</el-form-item>
					</el-col>
					<el-col :span="3">
						<el-form-item label-width="0">
							<el-input v-model="field.desc" placeholder="描述"></el-input>
						</el-form-item>
					</el-col>
					<el-col :span="1">
						<el-form-item label-width="0">
							<el-button type="danger">删除</el-button>
						</el-form-item>
					</el-col>
				</el-row>
			</template>
			<el-row>
				<el-col :span="24">
					<el-form-item>
						<el-button style="width: 100%" @click="addField">添加字段</el-button>
					</el-form-item>
				</el-col>
			</el-row>

			<el-form-item>
				<el-button type="danger" @click="$emit('update:visible', false)">取消</el-button>
				<el-button type="primary" @click="addCategory">添加</el-button>
			</el-form-item>
		</el-form>
	</el-dialog>
</template>

<script>
import {GetCategoryDetail} from '@/api/index'
export default {
	props: ['visible', 'id'],
	emits: ['update:visible', 'upload'],
	beforeCreate() {
		if (this.id === null) {
			console.log('id is null')
			return true
		}
		GetCategoryDetail(this.id).then((response) => {
			console.log(response)
			this.categoryInfo.category = response.category
			this.categoryInfo.fields = response.fields
		})
	},
	data() {
		return {
			categoryInfo: {
				category: {
					name: null,
					alias: null,
					desc: null
				},
				fields: []
			},
		}
	},
	methods: {
		addCategory() {
			console.log('增加资产')
			console.log(this.categoryInfo)
			this.$emit('update:visible', false)
			this.$emit('upload', this.categoryInfo)
		},
		addField() {
			this.categoryInfo.fields.push({
				name: null,
				desc: null,
				type: null,
				need: null,
				multi: null,
				show: null,
				category_id: this.categoryInfo.category.id
			})
		},
		switchChange(val) {
			console.log(val)
		}
	},
}
</script>

<style>
</style>

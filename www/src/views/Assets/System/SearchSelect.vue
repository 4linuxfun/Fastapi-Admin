<template>
	<el-row>
		<el-col :span="8">
			<el-select v-model="selectField" filterable remote reserve-keyword placeholder="选择字段"
				:remote-method="searchFields" :loading="loading" value-key="name">
				<el-option v-for="field in fields" :key="field.name" :label="field.name" :value="field"></el-option>
			</el-select>
		</el-col>
		<el-col :span="4">
			<el-select v-model="select.type" placeholder="请选择" style="width: 100px;">
				<template v-if="selectField.type == 'text'">
					<el-option value="like" label="包含"></el-option>
				</template>
				<template v-else>
					<el-option value="eq" label="等于"></el-option>
					<el-option value="ne" label="不等于"></el-option>
					<el-option value="gt" label="大于"></el-option>
					<el-option value="ge" label="大于等于"></el-option>
					<el-option value="lt" label="小于"></el-option>
					<el-option value="le" label="小于等于"></el-option>
				</template>
				
			</el-select>
		</el-col>
		<el-col :span="8">
			<el-input v-model="select.value" placeholder="请输入条件" @change="returnFilter" :type="select.type"></el-input>
		</el-col>
		<el-button type="danger" size="mini" circle @click="$emit('delete')"><el-icon><minus /></el-icon></el-button>

	</el-row>

</template>

<script>
	import {Minus} from '@element-plus/icons'
	export default {
		components: {
			Minus,
		},
		props:['category_id','filter'],
		emits:['add','update:filter','delete'],
		data() {
			return {
				select: this.filter,
				selectField:{},
				fields: [],
				loading: false,
			}
		},
		methods: {
			searchFields(query) {
				if (query !== ''){
					this.loading = true
					this.$request({
						url:'/api/assets/category_field',
						method: 'get',
						params:{
							category_id:this.category_id,
							query:query
						}
					}).then((response)=>{
						console.log(response)
						this.fields = response
						this.loading = false
					})
				} else {
					this.fields = []
				}
			},
			returnFilter(){
				console.log(this.selectField)
				
				this.select.field = this.selectField.name
				if(this.selectField.type === 'number'){
					this.select.value = Number(this.select.value)
				}
				console.log(this.select)
				this.$emit('update:filter',this.select)
			}
		},
	}
</script>

<style>
</style>

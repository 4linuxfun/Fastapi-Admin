<template>
	<el-row>
		<el-col :span="8">
			<el-select v-model="filterInfo.field" filterable remote reserve-keyword placeholder="请选择"
				:remote-method="searchFields" :loading="loading" @change="updateFilter">
				<el-option v-for="field in fields" :key="field.name" :label="field.name" :value="field.name"></el-option>
			</el-select>
		</el-col>
		<el-col :span="4">
			<el-select v-model="filterInfo.mode" placeholder="请选择" style="width: 80px;">
				<template v-if="filterInfo.type === 'text'">
					<el-option value="like" label="包含"></el-option>
				</template>
				<template v-else>
					<el-option value="eq" label="="></el-option>
					<el-option value="ne" label="!="></el-option>
					<el-option value="gt" label=">"></el-option>
					<el-option value="ge" label=">="></el-option>
					<el-option value="lt" label="<"></el-option>
					<el-option value="le" label="<="></el-option>
				</template>

			</el-select>
		</el-col>
		<el-col :span="8">
			<input-plus :type="filterInfo.type" v-model:data="filterInfo.value"></input-plus>
		</el-col>
		<el-button class="mini-button" type="danger" size="mini" circle @click="$emit('delete')">
			<el-icon :size="5">
				<minus />
			</el-icon>
		</el-button>
	</el-row>

</template>

<script>
	import {
		Minus
	} from '@element-plus/icons-vue'
	import InputPlus from '@/components/InputPlus'
	import {
		SearchCategoryFields
	} from '@/api/fields'
	export default {
		components: {
			Minus,
			'input-plus': InputPlus,
		},
		props: ['category_id', 'filter'],
		emits: ['update:filter', 'delete'],
		data() {
			return {
				filterInfo:this.filter,
				fields: [],
				loading: false,
			}
		},
		// created() {
		// 	console.log('create searchSelect')
		// 	this.selectField.name = this.filter.field
		// },
		methods: {
			searchFields(query) {
				if (query !== '') {
					this.loading = true
					SearchCategoryFields(this.category_id, query).then((response) => {
						console.log(response)
						this.fields = response
						this.loading = false
					})
				} else {
					this.fields = []
				}
			},
			updateFilter(value){
				console.log('change value:'+value)
				for (let field of this.fields){
					console.log(field)
					if (field.name == value){
						this.filterInfo.mode = null
						this.filterInfo.type = field.type
						break
					}
				}
				console.log('update type:'+this.filterInfo.type)
			},
		},
	}
</script>

<style>
	.mini-button{
		height: 5px;
		margin-top: 5px;
	}
</style>

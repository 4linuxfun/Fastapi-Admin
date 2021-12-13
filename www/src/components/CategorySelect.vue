<template>
	<el-autocomplete v-model="selectCategory" :fetch-suggestions="querySearchAsync"
		:placeholder="placeholder" value-key="name" @select="handleSelect" clearable>
	</el-autocomplete>
</template>

<script>
	import {GetCategories} from '@/api/index'
	export default{
		props:['category','placeholder'],
		emits:['update:category','handleSelect'],
		data() {
			return {
				selectCategory: this.category
			}
		},
		methods: {
			async querySearchAsync(query, callback) {
				console.log('query:'+query)
				GetCategories(query).then((response) => {
					callback(response)
				}).catch((error)=>{
					this.$notify({
						title: 'error',
						message: error,
						type: 'error'
					})
				})
			},
			handleSelect(item) {
				// 选择后，就需要去后台捞取对应资产的动态字段，并进行列出选择
				console.log(item)
				this.$emit('update:category',this.selectCategory)
				this.$emit('handleSelect',item)
			},
		},
	}
</script>

<style>
</style>

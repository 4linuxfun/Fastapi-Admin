<template>
	<!-- 详细信息、单数据更新页面 -->
	<el-dialog :model-value="visible" :title="title" width="70%" @close="$emit('update:visible',false)"
		destroy-on-close>
		<table border="1" style="width: 100%;">
			<tr>
				<td>资产类型</td>
				<td>{{formData.category}}</td>
				<td>管理员</td>
				<td>{{formData.manager}}</td>
			</tr>
			<tr>
				<td>区域</td>
				<td>{{formData.area}}</td>
				<td>使用人</td>
				<td>{{formData.user}}</td>
			</tr>
			<template v-for="(item,index) in arrayData" :key="item">
				<tr v-if="index%2 == 0">
					<td>{{arrayData[index].name}}</td>
					<td>{{arrayData[index].value}}</td>
					<td>{{arrayData[index+1].name}}</td>
					<td>{{arrayData[index+1].value}}</td>
				</tr>
			</template>
		</table>
	</el-dialog>

</template>

<script>
	import request from '@/utils/request'
	export default {
		props: ['data', 'visible', "title", "disabled"],
		emits: ['update:data', 'reload', 'update:visible'],
		// created() {
		// 	console.log(this.data)
		// },
		mounted() {
			for(let [key,value] of Object.entries(this.formData)){
				if(key === 'info'){
					for(let [infoKey,infoValue] of Object.entries(value)){
						this.arrayData.push({name:infoKey,value:infoValue})
					}
				} 
			}
			console.log(this.arrayData)
		},
		data() {
			return {
				formData: this.data,
				arrayData: [],
			}
		},
		methods: {
			updateFields(fields) {
				console.log(fields)
				this.$emit('update:visible', false)
				this.$emit('reload')
				request({
					url: "/api/assets/update_category_detail",
					method: "post",
					data: fields
				}).then(() => {
					console.log('更新成功')
				})
			},
		},
	}
</script>

<style>
</style>

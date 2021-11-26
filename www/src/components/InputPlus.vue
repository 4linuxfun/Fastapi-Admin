<!-- 封装不同类型，选择不同的输入框 -->
<template>
	<el-input v-if="type=='text'" v-model="value" placeholder="请输入" @change="$emit('update:data',value)">
	</el-input>
	<el-input-number v-else-if="type=='number'" v-model="value" placeholder="请输入" style="width: 100%;" @change="$emit('update:data',value)">
	</el-input-number>
	<el-date-picker v-else-if="type=='date'" :type="type" v-model="value" placeholder="选择日期" value-format="YYYY-MM-DD"
		style="width: 100%;" @change="$emit('update:data',value)">
	</el-date-picker>
	<el-date-picker v-else-if="type=='datetime'" :type="type" v-model="value" placeholder="选择日期"
		value-format="YYYY-MM-DD HH:mm:ss" style="width: 100%;" @change="$emit('update:data',value)"></el-date-picker>
</template>

<script>
	export default {
		props: ['type', 'data'],
		emits: ['update:data'],
		data() {
			return {
				value: this.data,
			}
		},
	}
</script>

<style>
</style>

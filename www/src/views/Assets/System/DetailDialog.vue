<template>
	<!-- 导入模板Dialog -->
	<el-dialog :model-value="visible" title="数据详情" width="50%" @close="$emit('update:visible',false)" destroy-on-close>
		<el-form :model="formData">
			<el-row :gutter="20">
				<el-col span="8">
					<el-form-item label="主机名">
						<el-input v-model="formData.host"></el-input>
					</el-form-item>
				</el-col>
				<el-col span="8">
					<el-form-item label="IP地址">
						<el-input v-model="formData.ip"></el-input>
					</el-form-item>
				</el-col>
				<el-col span="8">
					<el-form-item label="操作系统">
						<el-input v-model="formData.system"></el-input>
					</el-form-item>
				</el-col>	
			</el-row>
			<el-row>
				<template v-for="(value,name) in formData.info" :key="name">
					<span>{{name}}:{{value}}</span>
				</template>
				
			</el-row>
		</el-form>
		
	</el-dialog>
</template>

<script>
	import request from '@/utils/request'
	import {downloadFile} from '@/api/file'
	export default {
		props: ['data','visible'],
		emits: ['update:data','upload', 'update:visible'],
		data() {
			return {
				formData:this.data,
			}
		},
		methods: {
			// updateMenu() {
			// 	this.$emit('update',this.selectData)
			// 	this.$emit('cancel')
			// },
			handleChange(file, fileList){
				console.log(file)
				console.log(fileList)
				console.log(this.fileList)
				this.fileList = fileList
				console.log(this.fileList)
			},
			uploadFiles(file) {
				console.log('触发提交操作')
				console.log(file)
				// 前后端统一的字段名“files”，如果需要调整，前后端统一
				this.formData.append("files",file.file)
				
			},
			handleUpload() {
				console.log('点击上传')
				// 通过点击按钮手动调用上传函数 handleUpload ，创建一个 FormData, 调用 upload 组件的 submit 方法的时候会循环调用 http-request 配置的方法，从而往 FormData 里存放文件。
				this.formData = new FormData()
				this.$refs.upload.submit()
				const post = request({
					url:"/api/assets/system/import",
					method:"post",
					data:this.formData
				})
				this.$emit('upload',post)
				this.$emit('update:visible',false)
			},
			downloadTemp(){
				console.log('下载模板')
				downloadFile("/api/assets/system/down_temp","get")
			}

		},
	}
</script>

<style>
</style>


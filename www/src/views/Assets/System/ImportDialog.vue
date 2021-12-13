<template>
	<!-- 导入模板Dialog -->
	<div>
		<el-dialog :model-value="visible" title="数据导入" width="30%" @close="$emit('update:visible',false)" destroy-on-close>
			<el-space size="large">
				<el-button type="info" size="medium" @click="importDialog=true">模板下载</el-button>
				<el-upload ref="upload" action="" :file-list="fileList" :on-change="handleChange" :http-request="uploadFiles" :auto-upload="false" multiple>
					<template #trigger>
						<el-button type="primary" size="medium">添加文件</el-button>
					</template>
					<el-button type="success" size="medium" @click="handleUpload">上传</el-button>
				</el-upload>
			</el-space>
			
		</el-dialog>
	</div>
	
	<el-dialog :model-value="importDialog" title="选择资产类型" width="20%" @close="importDialog = false" destroy-on-close>
		<category-select style="width: 100%;" v-model:category="category" placeholder="资产类型" @handleSelect="handleSelect"></category-select>
		<el-button type="primary" size="small" @click="downloadTemp">下载</el-button>
	</el-dialog>
	
</template>

<script>
	import {ImportFile} from '@/api/index'
	import {downloadFile} from '@/api/file'
	import CategorySelect from '@/components/CategorySelect'
	export default {
		components: {
			'category-select':CategorySelect,
		},
		props: ['visible'],
		emits: ['upload', 'update:visible'],
		data() {
			return {
				fileList: [],
				formData:'',
				importDialog:false,
				category:null,
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
				const post = ImportFile(this.formData)
				this.$emit('upload',post)
				this.$emit('update:visible',false)
			},
			downloadTemp(){
				console.log('下载模板')
				downloadFile("/api/assets/system/down_temp/"+this.category,"get")
				this.importDialog = false
			},
			handleSelect(item){
				this.category = item.id
			}

		},
	}
</script>

<style>
</style>

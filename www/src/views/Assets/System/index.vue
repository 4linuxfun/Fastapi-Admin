<template>
	<el-row>
		<el-form :model="searchForm" inline="true">
			<el-form-item label="项目">
				<el-input v-model="searchForm.project"></el-input>
			</el-form-item>
			<el-form-item label="IP地址">
				<el-input v-model="searchForm.ip"></el-input>
			</el-form-item>
			<el-form-item label="主机名">
				<el-input v-model="searchForm.host"></el-input>
			</el-form-item>
			<el-form-item label="类型">
				<el-select v-model="searchForm.type" placeholder="虚拟机">
					<el-option value="物理机"></el-option>
					<el-option value="虚拟机"></el-option>
				</el-select>
			</el-form-item>
			<el-form-item>
				<el-button type="primary" @click="handleSearch">搜索</el-button>
			</el-form-item>
			<el-form-item>
				<el-button type="primary" @click="importDialog=true">导入</el-button>				
			</el-form-item>
			<el-form-item>
				<el-button type="primary" @click="handleOutput">导出</el-button>
			</el-form-item>
		</el-form>
		
	</el-row>
	
	<el-table :data="systemData" :border="true">
		<el-table-column prop="id" label="ID" width="50"></el-table-column>
		<el-table-column prop="host" label="主机名"></el-table-column>
		<el-table-column prop="ip" label="IP地址"></el-table-column>
		<el-table-column prop="system" label="操作系统"></el-table-column>
		<el-table-column prop="cpu" label="CPU数量"></el-table-column>
		<el-table-column prop="storage" label="空间(G)"></el-table-column>
		<el-table-column prop="memory" label="内存(G)"></el-table-column>
		<el-table-column prop="admin" label="管理员"></el-table-column>
		<el-table-column prop="env" label="环境"></el-table-column>
		<el-table-column prop="type" label="类型"></el-table-column>
		<el-table-column prop="project" label="项目"></el-table-column>
		<el-table-column prop="developer" label="三线开发"></el-table-column>
		<el-table-column fixed='right' label="详情">
			<template #default="scope">
				<el-button type="text" size="small" @click="handleView(scope.row.id)">详情</el-button>
			</template>
		</el-table-column>
	</el-table>
	<el-pagination background layout="prev,pager,next" :total="total" :current-page="currentPage" @update:current-page="handlePage" hide-on-single-page="true" prev-text="上一页" next-text="下一页"></el-pagination>
	
	<div v-if="importDialog">
		<import-dialog v-model:visible="importDialog" @upload="uploadResponse"></import-dialog>
	</div>

</template>

<script>
	import request from '@/utils/request'
	import ImportDialog from './ImportDialog'
	import {downloadFile} from '@/api/file'
	export default {
		components:{
			'import-dialog':ImportDialog,
		},
		data() {
			return {
				searchForm: {
					project:'',
					ip:'',
					host:'',
					type:'',
					limit:10,
					offset:0,
				},
				systemData:"",
				total:0,
				currentPage:1,
				importDialog:false
			}
		},
		methods: {
			requestData(){
				request({
					url:'/api/assets/system/search',
					method:'post',
					data:this.searchForm
				}).then((response)=>{
					this.systemData = response
				})
			},
			handleSearch() {
				request({
					url:'/api/assets/system/search_total',
					method:'post',
					data:this.searchForm
				}).then((response)=>{
					this.total=response
					this.currentPage = 1
					this.searchForm.offset = 0
					this.requestData()
				})
				
				
			},
			handlePage(newPage){
				console.log(newPage)
				this.currentPage = newPage
				this.searchForm.offset = (this.currentPage-1)*10
				this.requestData()
			},
			handleView(id){
				console.log('显示详情'+id)
			},
			uploadResponse(request){
				request.then(()=>{
					this.$notify({
						title:'success',
						message:'上传成功',
						type:'success'
					})
				}).catch((err)=>{
					console.log('上传失败'+err)
				})
			},
			handleOutput(){
				downloadFile("/api/assets/system/output","post",this.searchForm)
			}
			
		},
	}
</script>

<style>
</style>

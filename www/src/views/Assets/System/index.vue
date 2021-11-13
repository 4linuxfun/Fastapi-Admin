<template>
	<el-row>
		<el-form :model="searchForm" inline="true">
			<el-row>
				<el-form-item label="资产类型">
					<el-autocomplete v-model="searchForm.category" :fetch-suggestions="querySearchAsync" placeholder="资产类型"
						value-key="name"
						@select="handleSelect">
					</el-autocomplete>
				</el-form-item>
				<el-form-item label="管理员">
					<el-input v-model="searchForm.manager"></el-input>
				</el-form-item>
				<el-form-item label="区域">
					<el-input v-model="searchForm.area"></el-input>
				</el-form-item>
				<el-form-item label="使用人">
					<el-input v-model="searchForm.user"></el-input>
				</el-form-item>
				<el-form-item>
					<el-button type="primary" @click="handleSearch">搜索</el-button>
				</el-form-item>
				<el-form-item v-if="$route.meta.import === true">
					<el-button type="primary" @click="importDialog=true">导入</el-button>
				</el-form-item>
				<el-form-item v-if="$route.meta.output === true">
					<el-button type="primary" @click="handleOutput">导出</el-button>
				</el-form-item>
			</el-row>
			<el-row>
				<template v-for="field in fields" :key="field.id">
					<el-form-item :label="field.desc">
						<el-input v-model="searchForm.info[[field.name]]"></el-input>
					</el-form-item>
				</template>
				
			</el-row>
			
		</el-form>

	</el-row>

	<el-table :data="systemData" :border="true">
		<el-table-column type="index" label="ID" width="50"></el-table-column>
		<el-table-column prop="category" label="资产类型"></el-table-column>
		<el-table-column prop="manager" label="管理员"></el-table-column>
		<el-table-column prop="area" label="区域"></el-table-column>
		<el-table-column prop="user" label="使用人"></el-table-column>
		<template v-for="field in fields" :key="field.id">
			<!-- <span>{{field}}</span> -->
			<el-table-column :label="field.desc" v-if="field.show">
				<template #default="scope">
					{{scope.row.info[field.name]}}
				</template>
			</el-table-column>
			
		</template>
		<el-table-column fixed='right' label="详情">
			<template #default="scope">
				<el-button type="text" size="small" @click="handleDetail(scope.row)">详情</el-button>
			</template>
		</el-table-column>
	</el-table>
	<el-pagination background layout="prev,pager,next" :total="total" :current-page="currentPage"
		@update:current-page="handlePage" hide-on-single-page="true" prev-text="上一页" next-text="下一页"></el-pagination>

	<div v-if="importDialog">
		<import-dialog v-model:visible="importDialog" @upload="uploadResponse"></import-dialog>
	</div>
	<div v-if="detailDialog">
		<detail-dialog v-model:data="showData" v-model:visible="detailDialog" @upload="uploadResponse"></detail-dialog>
	</div>

</template>

<script>
	import request from '@/utils/request'
	import ImportDialog from './ImportDialog'
	import DetailDialog from './DetailDialog'
	import {
		downloadFile
	} from '@/api/file'
	export default {
		components: {
			'import-dialog': ImportDialog,
			'detail-dialog': DetailDialog
		},
		data() {
			return {
				searchForm: {
					category: null,
					manager: null,
					area: null,
					user: null,
					info:{},
					limit: 10,
					offset: 0,
				},
				systemData: "",
				total: 0,
				currentPage: 1,
				importDialog: false,
				detailDialog: false,
				showData: '',
				fields:'',
			}
		},
		methods: {
			requestData() {
				console.log(this.searchForm)
				request({
						url: '/api/assets/system/search',
						method: 'post',
						data: this.searchForm
					}).then((response) => {
						console.log(response)
						this.systemData = response
				})
				
			},
			async querySearchAsync(query,callback){
				request({
					url:'/api/assets/category-list',
					method:'get'
				}).then((response)=>{
					callback(response)
				})
			},
			handleSelect(item){
				// 选择后，就需要去后台捞取对应资产的动态字段，并进行列出选择
				console.log(item)
				request({
					url:'/api/assets/category_field/'+item.id,
					method:'get',
				}).then((fieldList)=>{
					this.fields = fieldList
					for(let field of fieldList){
						let fieldName = field.name
						console.log(fieldName)
						this.searchForm.info[fieldName] = ''
					}
				})
			},
			handleSearch() {
				console.log(this.searchForm)
				request({
					url: '/api/assets/system/search_total',
					method: 'post',
					data: this.searchForm
				}).then((response) => {
					this.total = response
					this.currentPage = 1
					this.searchForm.offset = 0
					this.requestData()
				})


			},
			handlePage(newPage) {
				console.log(newPage)
				this.currentPage = newPage
				this.searchForm.offset = (this.currentPage - 1) * 10
				this.requestData()
			},
			handleDetail(info) {
				console.log('显示详情' + info)
				this.detailDialog = true
				this.showData = info
			},
			uploadResponse(request) {
				request.then(() => {
					this.$notify({
						title: 'success',
						message: '上传成功',
						type: 'success'
					})
				}).catch((err) => {
					console.log('上传失败' + err)
				})
			},
			handleOutput() {
				downloadFile("/api/assets/system/output", "post", this.searchForm)
			}

		},
	}
</script>

<style>
</style>

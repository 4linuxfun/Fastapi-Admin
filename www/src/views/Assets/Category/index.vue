<!-- 基础数据维护页面 -->
<template>
	<el-row>
		<el-col :span="6">
			<el-form :model="searchForm" inline="true">
				<el-form-item label="资产类型">
					<el-autocomplete v-model="searchForm.category" :fetch-suggestions="querySearchAsync" placeholder="资产类型"
						value-key="name"
						@select="handleSelect">
					</el-autocomplete>
				</el-form-item>
				<el-form-item>
					<el-button type="primary" @click="handleSearch">搜索</el-button>
				</el-form-item>
			</el-form>
		</el-col>
		<el-col :span="8">
			<el-button type="primary"  @click="addDialog">添加新资产</el-button>
		</el-col>
	</el-row>
	
	<el-table :data="categoryList" :border="true">
		<el-table-column prop="name" label="资产类型"></el-table-column>
		<el-table-column prop="alias" label="别名"></el-table-column>
		<el-table-column prop="desc" label="资产描述"></el-table-column>
		<el-table-column label="操作">
			<template #default="scope">
				<el-button type="primary" size="small" @click="handleEdit(scope.row.id)">修改</el-button>
				<el-button type="danger" size="small" @click="handleDel">删除</el-button>
			</template>
		</el-table-column>
	</el-table>
	<div v-if="categoryDialog">
		<category-dialog :id="categoryId" v-model:visible="categoryDialog" @upload="updateCategory"></category-dialog>
	</div>
	
</template>

<script>
	import request from '@/utils/request'
	import {GetAssets} from '@/api/assets'
	import {PostCategory} from '@/api/categories'
	import CategoryDialog from './CategoryDialog'
	export default {
		components:{
			'category-dialog':CategoryDialog,
		},
		data() {
			return {
				searchForm: {
					id:null,
					category: null,
				},
				categoryList: "",
				total: 0,
				currentPage: 1,
				categoryDialog: false,
				showData: '',
				fields:'',
				categoryId:null
			}
		},
		created() {
				this.init()
		},
		methods: {
			init(){
				request({
					url:'/api/categories',
					method:'get'
				}).then((response)=>{
					this.categoryList = response
				})
			},
			requestData() {
				console.log(this.searchForm)
				GetAssets(this.searchForm).then((response) => {
						console.log(response)
						this.systemData = response
				})
				
			},

			handleEdit(id){
				// 详情按钮，只读权限
				this.categoryDialog = true
				this.categoryId = id
			},
			handleSelect(item){
				// 选择后，就需要去后台捞取对应资产的动态字段，并进行列出选择
				console.log(item)
				console.log(this.searchForm)
				this.searchForm.id = item.id
			},
			handleSearch() {
				if (this.searchForm.category == null){
					this.$message({
						message:"请选择资产类型",
						type:"warning"
					})
					return false
				}
			},
			updateCategory(category){
				console.log(category)
				PostCategory(category).then(()=>{
					this.$notify({
								title:'success',
								message:"资产创建成功",
								type:'success'
							})
				}).catch(()=>{
						this.$notify({
							title:'success',
							message:"取消删除操作",
							type:'success'
						})
				})
				this.init()
			},
			addDialog(){
				this.categoryDialog = true
				this.categoryId = null
			}
		}	
	}
</script>

<style>
</style>

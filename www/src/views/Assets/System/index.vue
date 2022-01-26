<template>
	<div style="background-color: papayawhip;padding: 10px;">
		<el-row>
			<el-form :model="searchForm">
				<el-row>
					<el-form-item label="资产类型">
						<category-select v-model:category="searchForm.category" placeholder="资产类型"
							@handleSelect="handleSelect"></category-select>
						<!-- <el-autocomplete v-model="searchForm.category" :fetch-suggestions="querySearchAsync"
							placeholder="资产类型" value-key="name" @select="handleSelect">
						</el-autocomplete>-->
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
				</el-row>
			</el-form>
		</el-row>
		<el-row>
			<!-- <template v-for="field in fields" :key="field.id">
				<el-form-item :label="field.name">
					<el-input v-model="searchForm.info[[field.name]]"></el-input>
				</el-form-item>
			</template>-->
			<template v-for="(filter,index) in searchForm.filters" :key="filter.field">
				<search-select :category_id="searchForm.id" v-model:filter="searchForm.filters[index]"
					@delete="deleteFilter(index)"></search-select>
			</template>
			<el-button type="info" size="small" @click="addFilterSelect">增加条件</el-button>
		</el-row>
		<el-row>
			<el-button type="primary" @click="updateAssets">修改</el-button>
			<el-button type="primary" @click="handleAddOne">手动录入</el-button>
			<el-button v-if="$route.meta.import === true" type="primary" @click="importDialog = true">批量导入</el-button>
			<el-button v-if="$route.meta.output === true" type="primary" @click="handleOutput">批量导出</el-button>
		</el-row>
	</div>

	<el-table :data="systemData" :border="true" highlight-current-row @selection-change="handleSelectionChange"
		style="margin-top: 10px;">
		<el-table-column type="selection" width="55" />
		<el-table-column type="index" label="ID" width="50"></el-table-column>
		<el-table-column prop="category" label="资产类型"></el-table-column>
		<el-table-column prop="manager" label="管理员"></el-table-column>
		<el-table-column prop="area" label="区域"></el-table-column>
		<el-table-column prop="user" label="使用人"></el-table-column>
		<template v-for="field in fields" :key="field.id">
			<!-- <span>{{field}}</span> -->
			<el-table-column :label="field.name" v-if="field.show">
				<template #default="scope">{{ scope.row.info[field.name] }}</template>
			</el-table-column>
		</template>
		<el-table-column fixed="right" label="详情">
			<template #default="scope">
				<el-button type="text" size="small" @click="handleDetail(scope.row)">详情</el-button>
			</template>
		</el-table-column>
	</el-table>
	<el-pagination background layout="prev,pager,next" :total="total" :current-page="currentPage"
		@update:current-page="handlePage" :hide-on-single-page="true" prev-text="上一页" next-text="下一页"></el-pagination>

	<import-dialog v-if="importDialog" v-model:visible="importDialog" @upload="uploadResponse"></import-dialog>
	<detail-dialog v-if="detailDialog" :data="showData" v-model:visible="detailDialog"></detail-dialog>
	<update-dialog v-if="updateDialog" :data="showData" :fieldsInfo="fields" v-model:visible="updateDialog"
		@reload="handleSearch"></update-dialog>
	<multi-dialog v-if="multiDialog" v-model:data="showData" v-model:visible="multiDialog" :category="searchForm.id"
		@reload="handleSearch"></multi-dialog>
	<!-- <add-dialog v-if="addDialog.show" v-model:visible="addDialog.show" @reload="handleSearch" :title="addDialog.title">
	</add-dialog> -->
	<auto-from-dialog v-if="addDialog.show" v-model:visible="addDialog.show" :col="2" :formItemInfo="testFormItemInfo"
		@update="handleUpdate" :title="addDialog.title">
	</auto-from-dialog>
</template>

<script>
	import {
		GetCategoryFields
	} from '@/api/categories'
	import {
		GetAssetsCount,
		GetAssets
	} from '@/api/assets'
	import ImportDialog from './ImportDialog'
	import DetailDialog from './DetailDialog'
	import MultiDialog from './MultiDialog'
	// import AddDialog from './AddDialog'
	import UpdateDialog from './UpdateDialog'
	import AutoFormDialog from '@/components/AutoFormDialog'
	import CategorySelect from '@/components/CategorySelect'
	import SearchSelect from './SearchSelect'
	import {
		downloadFile
	} from '@/api/file'
	import {
		reactive,
		ref,
		computed,
		watch
	} from 'vue'
	import {
		ElMessage
	} from 'element-plus'
	export default {
		components: {
			'import-dialog': ImportDialog,
			'detail-dialog': DetailDialog,
			'multi-dialog': MultiDialog,
			// 'add-dialog': AddDialog,
			'category-select': CategorySelect,
			'search-select': SearchSelect,
			'update-dialog': UpdateDialog,
			'auto-from-dialog': AutoFormDialog
		},
		setup() {
			const initSearchForm = () => {
				return {
					id: null,
					category: null,
					manager: null,
					area: null,
					user: null,
					// info中存放的时
					info: {},
					limit: 10,
					offset: 0,
					filters: [],
				}

			}
			const testFormData = reactive({
				"name": null,
				"path": null,
				"component": null,
				"date": null,
				"datetime": null,
				"age": 12,
				"value": true,
			})
			const testFormItemInfo = ref(
				[{
						"type": "text",
						"prop": "name",
						"value": null,
						"label": "菜单名",
						"rules": [{
							"required": true,
							"message": "请输入菜单名",
							"trigger": "blur"
						}],
						"properties": {
							"placeholder": "请输入菜单名",
						},
					},
					{
						"type": "number",
						"prop": "age",
						"value": 11,
						"label": "年龄",
						"rules": [{
							"required": true,
							"message": "请输入年龄",
							"trigger": "blur"
						}],
						"properties": {
							"placeholder": "请输入年龄",
						},
					},
					{
						"type": "switch",
						"prop": "value",
						"value": true,
						"label": "值",
						"rules": [{
							"required": true,
							"message": "请输入值",
							"trigger": "blur"
						}],

					},
					{
						"type": "text",
						"prop": "path",
						"value": null,
						"label": "链接地址",
						"rules": [{
							"required": true,
							"message": "'/'开头",
							"trigger": "blur"
						}],
						"properties": {
							"placeholder": "'/'开头",
						}
					},
					{
						"type": "text",
						"prop": "component",
						"value": null,
						"label": "组件",
						"rules": [{
							"required": true,
							"message": "参考前端组件填写",
							"trigger": "blur"
						}],
						"properties": {
							"placeholder": "参考前端组件填写",
						}
					},
					{
						"type": "date",
						"prop": "date",
						"value": "2021-11-12",
						"label": "创建时间",
						"rules": [{
							"required": true,
							"message": "参考前端组件填写",
							"trigger": "blur"
						}],
						"properties": {
							"type": 'date',
							"placeholder": '请输入日期',
							"value-format": "YYYY-MM-DD"
						},
					},
					{
						"type": "datetime",
						"prop": "datetime",
						"value": "2021-12-12 12:12:12",
						"label": "申报时间",
						"rules": [{
							"required": true,
							"message": "参考前端组件填写",
							"trigger": "blur"
						}],
						"properties": {
							"type": 'datetime',
							"placeholder": '请输入时间',
							"value-format": "YYYY-MM-DD HH:mm:ss",
							"style": "width: 100%;"
						},
					}
				])
			const systemData = ref([])
			const total = ref(0)
			const currentPage = ref(1)
			const importDialog = ref(false)
			const detailDialog = ref(false)
			const updateDialog = ref(false)
			const addDialog = reactive({
				show: false,
				title: '',
			})
			const showData = ref('')
			const fields = ref('')
			const selected = reactive([])
			const multiDialog = ref(false)
			const searchForm = reactive(initSearchForm())

			const resetSearchForm = () => {
				console.log(searchForm)
				console.log('init searchForm');
				Object.assign(searchForm, initSearchForm())
				console.log(searchForm)
			}
			const requestData = () => {
				console.log(searchForm)
				GetAssets(searchForm).then((response) => {
					console.log(response)
					systemData.value = response
					console.log('显示数据')
					console.log(systemData);
				})

			}

			const handleUpdate = (value) => {
				console.log(value)
			}

			const handleSelect = (item) => {
				// 选择后，就需要去后台捞取对应资产的动态字段，并进行列出选择
				console.log(item)
				searchForm.id = item.id
				searchForm.info = {}
				GetCategoryFields(item.id).then((fieldList) => {
					fields.value = fieldList
					for (let field of fieldList) {
						let fieldName = field.name
						searchForm.info[fieldName] = ''
					}
					systemData.value = []
				})
			}

			const handleSearch = () => {
				console.log(searchForm)
				if (searchForm.category == null) {
					ElMessage({
						message: '未选择资产',
						type: 'warning'
					})
					return false
				}
				GetAssetsCount(searchForm).then((response) => {
					total.value = response
					currentPage.value = 1
					searchForm.offset = 0
					requestData()
				})


			}

			const category = computed(() => {
				return searchForm.category
			})

			// 监听category，如果变更，则重置查询列表
			watch(category, () => {
				const newId = searchForm.id
				const newCategory = searchForm.category
				resetSearchForm()
				searchForm.id = newId
				searchForm.category = newCategory
				total.value = 0
			})
			return {
				testFormData,
				testFormItemInfo,
				searchForm,
				systemData,
				total,
				currentPage,
				importDialog,
				detailDialog,
				updateDialog,
				addDialog,
				showData,
				fields,
				selected,
				multiDialog,
				resetSearchForm,
				requestData,
				handleSelect,
				handleSearch,
				handleUpdate
			}
		},

		methods: {
			testUpdate(data) {
				console.log('测试更新')
				console.log(data)
			},

			handlePage(newPage) {
				console.log(newPage)
				this.currentPage = newPage
				this.searchForm.offset = (this.currentPage - 1) * 10
				this.requestData()
			},
			handleDetail(info) {
				console.log('显示详情')
				console.log(info)
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
				if (this.searchForm.category === null) {
					this.$message({
						message: '请选择资产类型',
						type: 'warning'
					})
					return false
				}
				downloadFile("/api/assets/system/output", "post", this.searchForm)
			},
			handleSelectionChange(val) {
				console.log(val)
				this.selected = val
				console.log(this.selected)
			},
			updateAssets() {
				// 批量更新的触发按钮，但是还需要判断，单选则全局可变，多选则只能批量跟新单个值
				console.log(this.selected.length)
				console.log(this.detailDialog)
				if (this.selected.length == 1) {
					console.log('单选')
					this.showData = this.selected[0]
					this.updateDialog = true
					console.log(this.showData)
				} else if (this.selected.length >= 2) {
					console.log('多选')
					this.multiDialog = true
					this.showData = this.selected
				} else {
					this.$message({
						message: '未选择资产',
						type: 'warning'
					})
					// return false
				}
				this.requestData()
			},

			handleAddOne() {
				// 处理手动录入按钮事件
				this.addDialog.show = true
				this.addDialog.title = "数据添加"
			},
			addFilter(filter) {
				console.log(filter)
				if (filter.field !== null) {
					console.log('add filter to filters')
					console.log(this.searchForm.filters)
					this.searchForm.filters.push(filter)
					console.log(this.searchForm.filters)
				}

			},
			addFilterSelect() {
				console.log('click add filter button')
				this.searchForm.filters.push({
					field: null,
					type: 'text',
					mode: null,
					value: null
				})
			},
			deleteFilter(index) {
				console.log('delete index:' + index)
				this.searchForm.filters.splice(index, 1)
				// this.searchForm.filters[index] = null
				console.log(this.searchForm)
			}

		},
	}
</script>

<style>
	.el-form-item {
		margin-bottom: 0;
		margin-left: 10px;
	}

	.el-row {
		padding: 2px;
	}
</style>

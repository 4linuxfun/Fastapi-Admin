<!-- 多选状态的批量修改对话框 -->
<template>
	<div>
		<el-dialog :model-value="visible" title="批量修改" width="30%" @close="$emit('update:visible',false)" destroy-on-close>
			<el-form model="updateAssets">
				<template v-for="asset in updateAssets" :key="asset">
					<el-form-item>
						<template #label>
							<el-select v-model="asset.name" placeholder="Select">
								<el-option-group v-for="group in categoryDetail" :key="group.label" :label="group.label">
									<el-option v-for="item in group.options" :key="item.value" :label="item.label"
										:value="item.value">
									</el-option>
								</el-option-group>
							</el-select>
						</template>
						<el-input v-model="asset.value" placeholder="新值"></el-input>
					</el-form-item>
				</template>
		
				<el-row>
					<el-button style="width: 100%;" @click="addField">增加</el-button>
				</el-row>
				<el-form-item>
					<el-button type="danger" @click="$emit('update:visible',false)">取消</el-button>
					<el-button type="primary" @click='handleUpdate'>更新</el-button>
				</el-form-item>
			</el-form>
		
		</el-dialog>
	</div>
	

</template>

<script>
	import request from '@/utils/request'
	export default {
		props: ['data', 'visible', 'category'],
		emits: ['reload', 'update:visible'],
		mounted() {
			console.log(this.category)
			request({
				url: "/api/assets/asset_field/" + this.category,
				method: 'get'
			}).then((response) => {
				console.log(response)
				this.categoryDetail = response
			}).catch((error)=>{
				this.notify({
					message:error,
					title:'ERROR',
					type:'warning'
				})
			})

		},
		data() {
			return {
				categoryDetail: null,
				selectAssets: this.data,
				updateAssets: [],
				selectValue: null
			}
		},
		methods: {
			addField() {
				this.updateAssets.push({})
			},
			handleUpdate() {
				let assetsIdList = []
				console.log(this.selectAssets)
				for (let asset of this.selectAssets) {
					console.log(asset)
					assetsIdList.push(asset.id)
				}
				let updateInfo = {
					assets: assetsIdList,
					update: this.updateAssets
				}
				console.log(updateInfo)
				request({
					url: '/api/assets/update_assets',
					method: 'post',
					data: updateInfo
				}).then(() => {
					this.$notify({
						title: 'success',
						message: "资产更新成功",
						type: 'success'
					})
				}).catch(() => {
					this.$notify({
						title: 'warning',
						message: "资产更新失败",
						type: 'success'
					})
				})
				this.$emit('update:visible', false)
				this.$emit('reload')
			}
		},
	}
</script>

<style>
</style>

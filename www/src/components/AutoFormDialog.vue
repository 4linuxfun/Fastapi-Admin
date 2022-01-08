<template>
	<!-- 自动Form表单提交的模板 -->
	<el-dialog :model-value="visible" :title="title" :width="dialogWidth" @close="$emit('update:visible', false)">
		<el-form :model="formData" :label-width="labelWidth" :rules="rules" size="large">
			<el-row>
				<el-col :span="colSpan" v-for="item of formItemInfo" :key="item.prop">
					<el-form-item :label="item.label" :prop="item.prop" style="margin-bottom: 25px;">
						<component :is="item.type" v-model="formData[item.prop]" v-bind="componentAttrs[item.prop]">
						</component>
					</el-form-item>
				</el-col>
			</el-row>
		</el-form>
		<el-row justify="center">
			<el-button type="danger" @click="$emit('update:visible', false)">取消</el-button>
			<el-button type="primary" @click="handleUpdate">提交</el-button>
		</el-row>
	</el-dialog>
</template>

<script>
	import {
		ref,
		toRefs,
		reactive,
		computed
	} from "vue"
	import {
		ElInput,
		ElInputNumber,
		ElSwitch,
		ElDatePicker,
		ElTimePicker
	} from "element-plus"

	/**  
	 * 动态表单组件  
	 * @description 动态表单组件
	 * @tutorial 无  
	 * @property {Boolean} visible 是否显示formdialog  
	 * @property {String} title = "更新" 自定义表单抬头 
	 * @property {Number} col = [1|2] 显示列数
	 * @property {String} labelWidth = "100px" formItem label的宽度
	 * @property {Array} formItemInfo 表单各字段的属性  
	 * @event {Function} update 提交事件，返回新值  
	 * @example 
	 */
	export default {
		name: "AutoFormDialog",
		components: {
			"text": ElInput,
			"number": ElInputNumber,
			"switch": ElSwitch,
			"date": ElDatePicker,
			"datetime": ElDatePicker,
			"time": ElTimePicker,
		},
		props: {
			visible: {
				type: Boolean,
				default: false,
			},
			col: {
				type: Number,
				default: 1
			},
			title: {
				type: String,
				default: "更新"
			},
			labelWidth: {
				type: String,
				default: "100px",
			},
			formItemInfo: {
				type: Array,
			}
		},
		emits: ["update:visible", "update"],
		setup(props, {
			emit
		}) {
			const {
				formItemInfo,
				col
			} = toRefs(props)

			const formData = reactive({})
			const componentAttrs = reactive({})
			const rules = reactive({})

			formItemInfo.value.forEach((v) => {
				formData[v.prop] = v.value
				componentAttrs[v.prop] = v.properties
				rules[v.prop] = v.rules
			})

			// 根据col属性判断，1列 则默认30%，2列则50%
			const dialogWidth = (col.value == 1) ? ref('30%') : ref('50%')

			const colSpan = computed(() => {
				return (col.value == 1) ? 24 : 12
			})

			const handleUpdate = () => {
				emit("update", formData)
				emit('update:visible', false)
			}

			return {
				dialogWidth,
				colSpan,
				formData,
				componentAttrs,
				rules,
				handleUpdate
			}
		},
	}
</script>

<style>
</style>

<template lang="">

    <el-row style="width:300px" :gutter="5">
		<el-col :span="18">
			<el-input v-model="search"  placeholder="搜索" clearable @clear="init">
				<template #append>
					<el-button @click="searchApis"><el-icon><search /></el-icon></el-button>
				</template>
			</el-input>
		</el-col>
		<el-col :span="6">
			<el-button  type="primary"  @click="handleEdit(null)">新建接口</el-button>
		</el-col>
	</el-row>
    <div style="padding-top:10px">
        <el-table :data="apiList" border>
            <el-table-column prop="name" label="接口名"></el-table-column>
            <el-table-column prop="path" label="接口匹配"></el-table-column> 
            <el-table-column prop="enable" label="是否可用">
                <template #default="scope">
                    <el-tag :type="scope.row.enable?'success':'danger'" effect="dark">{{scope.row.enable?'启用':'禁用'}}</el-tag>
                </template>
            </el-table-column> 
            <el-table-column label="操作">
                <template #default="scope">
                    <el-button type="primary" @click="handleEdit(scope.row)">编辑</el-button>
                    <el-button type="danger" @click="handleDel(scope.row.id)">删除</el-button>
                </template>
            </el-table-column>
        </el-table>
    </div>

    <div v-if="dialogVisible">
		<add-dialog :data='selectApi' v-model:visible='dialogVisible'></add-dialog>
	</div>
    
</template>
<script>
import { ref, watch } from "vue"
import { Search } from '@element-plus/icons-vue'
import { GetApis, DelApis } from '@/api/sysApi'
import AddDialog from './AddDialog'
import { ElMessage } from "element-plus"
export default {
    components: {
        Search,
        AddDialog,
    },
    setup() {
        const apiList = ref([])
        const search = ref('')
        const dialogVisible = ref(false)
        const selectApi = ref(null)

        const init = () => {
            console.log('start to init');
            GetApis().then((response) => {
                apiList.value = response
            })
        }
        const searchApis = () => {
            GetApis(search.value).then((response) => {
                apiList.value = response
            })
        }
        const handleEdit = (api) => {
            selectApi.value = api
            dialogVisible.value = true
        }
        const handleDel = (id) => {
            DelApis(id).then(() => {
                ElMessage({ message: '删除接口成功', type: 'success' })
            }).catch((error) => { ElMessage({ message: '删除接口失败：' + error, type: 'error' }) 
            }).finally(()=>{
                init()
            })
            
        }

        watch(dialogVisible, () => { init() })

        init()
        return {
            apiList,
            search,
            dialogVisible,
            selectApi,
            init,
            searchApis,
            handleEdit,
            handleDel
        }
    }
}
</script>
<style lang="">
    
</style>
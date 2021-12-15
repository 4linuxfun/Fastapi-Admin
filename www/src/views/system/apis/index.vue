<template lang="">

    <el-row style="width:300px" :gutter="5">
		<el-col :span="18">
			<el-input v-model="search"  placeholder="搜索" clearable>
				<template #append>
					<el-button @click="searchApis"><el-icon><search /></el-icon></el-button>
				</template>
			</el-input>
		</el-col>
		<el-col :span="6">
			<el-button  type="primary"  @click="handleAdd(null)">新建接口</el-button>
		</el-col>
	</el-row>
    <div style="padding-top:10px">
        <el-table :data="apiList" border>
            <el-table-column prop="name" label="接口名"></el-table-column>
            <el-table-column prop="path" label="接口匹配"></el-table-column> 
            <el-table-column prop="enable" label="是否可用"></el-table-column> 
            <el-table-column label="操作">
                <template #default>
                    <el-button>编辑</el-button>
                    <el-button>删除</el-button>
                </template>
            </el-table-column>
        </el-table>
    </div>
    
</template>
<script>
import { ref } from "vue"
import { Search } from '@element-plus/icons-vue'
import { GetApis } from '@/api/sysApi'
export default {
    components: {
        Search,
    },
    setup() {
        const apiList = ref([])
        const search = ref('')
        GetApis().then((response) => {
            apiList.value = response
        })

        const searchApis = () => {
            GetApis(search.value).then((response) => {
                apiList.value = response
            })
        }
        return {
            apiList,
            search,
            searchApis
        }
    }
}
</script>
<style lang="">
    
</style>
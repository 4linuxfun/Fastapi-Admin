<template lang="">
    <el-dialog :model-value="visible" :title="title" width="30%" @close="$emit('update:visible', false)">
        <el-form :model="form" label-width="120px">
            <el-form-item label="接口名">
                <el-input v-model="form.name"></el-input>
            </el-form-item>
            <el-form-item label="接口匹配">
                <el-input v-model="form.path">
                    <template #prepend>
                        <el-select v-model="apiType" placeholder="Select" style="width:110px">
                            <el-option value="GET"></el-option>
                            <el-option value="POST"></el-option>
                            <el-option value="PUT"></el-option>
                            <el-option value="DELETE"></el-option>
                        </el-select>
                    </template>
                </el-input>
            </el-form-item>
            <el-form-item label="是否启用">
                <el-switch v-model="form.enable" :active-value="1" :inactive-value="0"></el-switch>
            </el-form-item>
        </el-form>
        <el-button type="danger" @click="$emit('update:visible', false)">取消</el-button>
        <el-button v-if="form.id" type="primary" @click="handleUpdate">更新</el-button>
        <el-button v-else type="primary" @click="handleAdd">添加</el-button>
    </el-dialog>
</template>
<script>

import { ref, toRefs } from 'vue'
import { PostApis, PutApis } from '@/api/sysApi'
import { ElMessage } from 'element-plus'
export default {
    props: ['data', 'visible'],
    emits: ['update:visible'],
    setup(props, { emit }) {
        const title = ref('更新接口')
        const { data } = toRefs(props)
        console.log(data.value)
        const form = ref(Object.assign({}, data.value))
        if (data.value === null) {
            form.value = {
                id: null,
                name: null,
                path: null,
                enable: null
            }
            title.value = '新建接口'
        }
        const apiType = ref('')
        if (form.value.path !== null) {
            let pathList = form.value.path.split(':')
            apiType.value = pathList[0]
            form.value.path = pathList[1]
        }
        console.log(form)
        // 通用函数方法
        const handleAdd = () => {
            PostApis({ id: form.value.id, name: form.value.name, enable: form.value.enable, path: apiType.value + ':' + form.value.path }).then(() => {
                ElMessage({ message: '创建接口成功', type: "success" })
            }

            ).catch(() => {
                ElMessage({ message: '添加接口失败', type: "error" })
            }

            )
            emit('update:visible', false)
        }

        const handleUpdate = () => {
            PutApis({ id: form.value.id, name: form.value.name, enable: form.value.enable, path: apiType.value + ':' + form.value.path }).then(() => {
                ElMessage({ message: '更新接口成功', type: "success" })
            }

            ).catch(() => {
                ElMessage({ message: '更新接口失败', type: "error" })
            }

            )
            emit('update:visible', false)
        }

        return {
            form,
            apiType,
            title,
            handleAdd,
            handleUpdate
        }
    }

}
</script>
<style lang="">
    
</style>
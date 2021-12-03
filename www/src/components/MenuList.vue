<template>
    <el-menu
            class="el-menu-vertical-demo"
			router
            @open="handleOpen"
            @close="handleClose">
        <el-menu-item index="/dashboard">首页</el-menu-item>
        <template v-for="item in menuList" :key="item.name">
			<!-- 有子菜单时处理逻辑 -->
            <el-sub-menu v-if="item.children" :index="item.path">
                <template #title>
                    <span>{{item.name}}</span>
                </template>
                <template v-if="item.children">
                    <el-menu-item v-for="(children,index) in item.children" :key="index" :index="item.path + '/' + children.path">
                        {{children.name}}
                    </el-menu-item>
                </template>
            </el-sub-menu>
			<!-- 无子菜单时处理逻辑 -->
            <el-menu-item v-else :index="item.path" @click="handleOpen">
                {{item.name}}
            </el-menu-item>
        </template>

    </el-menu>
</template>

<script>
	import {useStore} from '@/stores'
	import {mapState} from 'pinia'
    export default {
        computed: {
			...mapState(useStore,{
				menuList:'asyncRoutes'
			})
        },
        methods: {
            handleOpen(key, keyPath) {
                console.log(key, keyPath);
            },
            handleClose(key, keyPath) {
                console.log(key, keyPath);
            }
        }
    }
</script>

<style>
    .el-menu-vertical-demo:not(.el-menu--collapse) {
        width: 200px;
        min-height: 100%;
    }
</style>
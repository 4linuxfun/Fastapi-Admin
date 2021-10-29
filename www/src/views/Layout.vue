<template>
	<div style="height: 100%">
		<el-container>
			<el-header>
				<header-content></header-content>
			</el-header>
			<el-container style="height: 100%">
				<el-aside width="200px">
					<menu-list></menu-list>
				</el-aside>
				<el-main>
					<router-view></router-view>
				</el-main>
			</el-container>
		</el-container>
	</div>
</template>

<script>
	import MenuList from '../components/MenuList';
	import HeaderContent from '@/components/HeaderContent';

	export default {
		name: "Layout",
		components: {
			'menu-list': MenuList,
			'header-content':HeaderContent,
		},
	}
</script>

<style>

</style>

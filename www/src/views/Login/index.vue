<template>
	<div class="login">
		<el-form ref="loginForm" :model="loginForm" :rules="loginRules" label-position="left" label-width="0px"
			class="login-form" @keyup.enter="handleLogin">
			<h3 class="title">资产管理系统</h3>
			<el-form-item prop="username">
				<el-input v-model="loginForm.username" type="text" auto-complete="off" placeholder="账号">
					<!-- <i class="el-icon-user-solid" style="height: 39px;width: 13px;margin-left: 2px;"></i> -->
				</el-input>
			</el-form-item>
			<el-form-item prop="password">
				<el-input v-model="loginForm.password" type="password" auto-complete="off" placeholder="密码">
					<!-- <i class="el-icon-lock" style="height: 39px;width: 13px;margin-left: 2px;"></i> -->
				</el-input>
			</el-form-item>
			<el-checkbox v-model="loginForm.rememberMe" style="margin: 0px 0px 25px 0px">记住账号</el-checkbox>
			<el-form-item style="width: 100%">
				<el-button :loading="loading" size="medium" type="primary" style="width: 100%" @click="handleLogin">
					<span v-if="!loading">登 录</span>
					<span v-else>登 录 中...</span>
				</el-button>
			</el-form-item>
		</el-form>
	</div>
</template>

<script>
	import Cookies from "js-cookie";
	import {
		mapActions
	} from "vuex"
	export default {
		name: "Login",
		data() {
			return {
				loginForm: {
					username: "",
					password: "",
					rememberMe: false,
				},
				loginRules: {
					username: [{
						required: true,
						trigger: "blur",
						message: "用户名不能为空"
					}, ],
					password: [{
						required: true,
						trigger: "blur",
						message: "密码不能为空"
					}, ],
				},
				loading: false,
				redirect: undefined,
			};
		},
		watch: {
			$route: {
				handler: function(route) {
					this.redirect = route.query && route.query.redirect;
				},
				immediate: true,
			},
		},
		created() {
			// 打开登录页面，就读取cookie信息，给username和rememberme赋值。。。需要吗？
			this.getCookie();
		},
		methods: {
			// 映射actions到本地
			...mapActions(['logIn']),
			getCookie() {
				const username = Cookies.get("username");
				const rememberMe = Cookies.get("rememberMe");
				this.loginForm = {
					username: username === undefined ? "" : username,
					rememberMe: rememberMe === undefined ? false : Boolean(rememberMe),
				};
			},
			handleLogin() {
				this.$refs.loginForm.validate((valid) => {
					const user = {
						username: this.loginForm.username,
						password: this.loginForm.password,
						rememberMe: this.loginForm.rememberMe,
					};
					console.log("start to do login");
					console.log(valid);
					if (valid) {
						this.loading = true;
						if (user.rememberMe) {
							Cookies.set("username", user.username, {
								expires: 1
							});
							Cookies.set("rememberMe", user.rememberMe, {
								expires: 1
							});
						} else {
							Cookies.remove("username");
							Cookies.remove("rememberMe");
						}
						console.log("dispatch login store actions");
						this.logIn(user)
							.then(() => {
								console.log("login ok,start to redirect to home");
								this.loading = false;
								this.$router.push({
									path: "/dashboard"
								});
							})
							.catch((error) => {
								this.loading = false;
								this.$notify({
									title:'错误！',
									message:error,
									type:'error'})
							});
					} else {
						console.log("提交错误!");
						return false;
					}
				});
			},
		},
	};
</script>

<style rel="stylesheet/scss" lang="scss">
	.login {
		display: flex;
		justify-content: center;
		align-items: center;
		// background-image:url('../../assets/login_images/1.jpg');
		height: 100%;
	}

	.title {
		margin: 0px auto 40px auto;
		text-align: center;
		color: #707070;
	}

	.login-form {
		border-radius: 6px;
		background: #99A9BF;
		width: 365px;
		padding: 25px 25px 5px 25px;

		.el-input {
			height: 38px;

			input {
				height: 38px;
			}
		}
	}

	.login-tip {
		font-size: 13px;
		text-align: center;
		color: #bfbfbf;
	}
</style>

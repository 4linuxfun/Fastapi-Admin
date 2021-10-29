# Bug列表
* 登录页面，不存在用户登录能继续执行后续的user_info请求
* 用户退出没有清理asyncRouter信息，导致下个用户登录不需要请求获取列表信息---logout增加清理asyncRouter
* 前端页面刷新导致vuex store信息丢失

# 功能需求
* 用户登录获取权限列表
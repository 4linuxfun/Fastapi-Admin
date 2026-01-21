# Token自动刷新功能说明

## 功能概述

本系统已实现token自动刷新功能，可以有效防止用户在操作过程中因token过期而被强制退出登录。

## 功能特性

### 后端功能

1. **Token刷新接口** (`/api/refresh`)
   - 验证当前token有效性
   - 生成新的token
   - 处理token过期异常

2. **Token过期检查**
   - 增强的JWT验证逻辑
   - 支持检查token剩余有效时间
   - 默认token有效期：30分钟

### 前端功能

1. **自动刷新机制**
   - 在token剩余时间少于5分钟时自动刷新
   - 避免重复刷新（1分钟内不重复刷新）
   - 防止并发刷新冲突

2. **请求拦截器集成**
   - 每次API请求前自动检查token状态
   - 自动刷新即将过期的token
   - 无缝集成，用户无感知

3. **Token管理器**
   - 定时检查token状态（每分钟检查一次）
   - 页面可见性变化时自动检查
   - 登录后自动启动，登出后自动停止

4. **错误处理**
   - token刷新失败时的友好提示
   - 自动跳转到登录页面
   - 完整的错误日志记录

## 使用方法

### 开发者

1. **无需额外配置**：功能已自动集成到现有的登录和请求流程中

2. **测试功能**：访问 `/token-test` 页面可以测试token自动刷新功能

3. **自定义配置**：
   ```javascript
   // 修改检查间隔（默认60秒）
   tokenManager.checkInterval = 30000 // 30秒
   
   // 修改刷新阈值（默认5分钟）
   // 在 shouldRefreshToken() 函数中修改 300000 毫秒
   ```

### 用户

1. **正常使用**：用户正常使用系统，无需关心token过期问题

2. **登录状态保持**：在token有效期内，系统会自动维持登录状态

3. **过期提醒**：如果token完全过期且无法刷新，系统会提示重新登录

## 技术实现

### 后端实现

```python
# 新增刷新接口
@router.post('/refresh', summary="刷新token")
async def refresh_token(request: Request, session: Session = Depends(get_session)):
    # 验证当前token并生成新token
    pass

# 增强的token检查函数
def check_token_expiry(token: str):
    # 检查token是否即将过期
    pass
```

### 前端实现

```javascript
// 自动刷新函数
export async function autoRefreshToken() {
    // 检查并刷新token
}

// Token管理器
class TokenManager {
    // 定时检查和刷新token
}

// 请求拦截器
service.interceptors.request.use(async config => {
    // 请求前自动检查并刷新token
})
```

## 配置参数

### 后端配置

- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token有效期（默认30分钟）
- 刷新阈值：剩余时间少于5分钟时触发刷新

### 前端配置

- 检查间隔：60秒
- 刷新阈值：5分钟
- 防重复刷新间隔：1分钟

## 安全考虑

1. **Token验证**：刷新时验证当前token的有效性
2. **用户状态检查**：确保用户账户仍然有效且未被禁用
3. **防重放攻击**：每次刷新生成全新的token
4. **错误处理**：完善的异常处理机制

## 故障排除

### 常见问题

1. **Token刷新失败**
   - 检查网络连接
   - 确认后端服务正常
   - 查看浏览器控制台错误信息

2. **频繁要求重新登录**
   - 检查系统时间是否正确
   - 确认token配置参数
   - 查看后端日志

3. **Token管理器未启动**
   - 确认已正常登录
   - 检查浏览器控制台是否有错误
   - 手动调用 `tokenManager.start()`

### 调试方法

1. **使用测试页面**：访问 `/token-test` 查看详细的token状态信息

2. **浏览器控制台**：查看token相关的日志输出

3. **网络面板**：监控 `/api/refresh` 接口的调用情况

## 更新日志

### v1.0.0
- 实现基础的token自动刷新功能
- 集成到现有的登录和请求流程
- 添加token管理器和测试页面
- 完善错误处理和用户提示

## 注意事项

1. **浏览器兼容性**：需要支持ES6+的现代浏览器
2. **网络环境**：在网络不稳定的环境下可能影响刷新效果
3. **并发请求**：系统已处理并发请求时的token刷新冲突
4. **存储方式**：token存储在Cookie中，请确保浏览器允许Cookie

## 联系支持

如果在使用过程中遇到问题，请：
1. 查看浏览器控制台错误信息
2. 使用 `/token-test` 页面进行诊断
3. 联系开发团队获取技术支持
# QQ OAuth 回调地址配置修复

## 问题描述

QQ OAuth 登录时出现错误：
```
redirect uri is illegal [appid: 102818448] (100010)
```

## 原因

1. **回调地址格式**：QQ互联要求回调地址不能有末尾斜杠
2. **白名单配置**：回调地址必须在QQ开放平台的应用设置中添加到白名单

## 已修复

### 1. 统一回调地址格式（移除末尾斜杠）

**修改前：**
```
https://app7626.acapp.acwing.com.cn/oauth/login/callback/qq/
```

**修改后：**
```
https://app7626.acapp.acwing.com.cn/oauth/login/callback/qq
```

### 2. 更新代码

- `backend/api/views/oauth/login.py`: 移除回调地址末尾斜杠
- `backend/api/url_patterns/oauth.py`: 添加无斜杠路由，保留有斜杠路由作为兼容

## 需要在QQ开放平台配置

### 步骤

1. **登录QQ开放平台**
   - 访问：https://connect.qq.com/
   - 登录你的QQ账号

2. **进入应用管理**
   - 点击"应用管理"
   - 选择你的应用（AppID: 102818448）

3. **添加回调地址**
   - 进入"应用详情" → "基本信息"
   - 找到"授权回调域"或"回调地址"设置
   - 添加以下回调地址：
     ```
     https://app7626.acapp.acwing.com.cn/oauth/login/callback/qq
     ```
   - **注意**：不要添加末尾斜杠

4. **保存配置**
   - 点击"保存"或"提交审核"（如果要求审核）

### 多个回调地址

如果还有其他QQ登录入口，也需要添加：
- `https://app7626.acapp.acwing.com.cn/qq/callback` (普通QQ登录)

### 重要提示

- QQ互联对回调地址格式要求**非常严格**
- 回调地址必须**完全匹配**（包括协议、域名、路径，不能有多余斜杠）
- 修改回调地址后可能需要等待几分钟生效
- 如果是新应用，可能需要提交审核

## 测试

配置完成后，测试步骤：

1. 访问OAuth授权页面
2. 点击"QQ登录"
3. 应该能正常跳转到QQ授权页面
4. 授权后应该能正常回调

## 如果还有问题

1. **检查回调地址是否完全一致**
   - 授权时的 `redirect_uri` 参数
   - 回调时的实际URL
   - QQ开放平台配置的白名单

2. **检查应用状态**
   - 确认应用已审核通过
   - 确认应用未过期
   - 确认AppID和AppKey正确

3. **查看日志**
   - Django日志中的QQ OAuth相关日志
   - 检查是否有其他错误信息


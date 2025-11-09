# 🚨 紧急部署指令

## 问题
Roamio 团队仍然遇到 500 错误，因为服务器还没部署修复代码。

## 修复代码
- Commit: 630c6f5
- 修复: `data` 变量在定义前使用

## 部署命令

### 方法 1: SSH 部署（需要手动登录服务器）

```bash
# 1. 登录服务器
ssh -p 20220 ppshuX@app7626.acapp.acwing.com.cn

# 2. 进入项目目录
cd ~/Ralendar

# 3. 拉取最新代码
git pull

# 4. 重启服务
sudo supervisorctl restart ralendar

# 5. 检查状态
sudo supervisorctl status ralendar

# 6. 查看日志
sudo supervisorctl tail -f ralendar stderr
```

### 方法 2: 使用 AcWing 部署工具

1. 登录 AcWing 控制台
2. 找到 app7626 应用
3. 点击"部署"按钮
4. 等待部署完成

## 验证部署

部署完成后，让 Roamio 重新测试：

```bash
# 测试请求
curl -X POST https://app7626.acapp.acwing.com.cn/api/v1/fusion/events/batch/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "测试事件",
    "start_time": "2025-11-10T10:00:00Z"
  }'
```

期望响应：200 OK，而不是 500 错误


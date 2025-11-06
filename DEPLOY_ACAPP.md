# AcWing 端部署指南

## 🚀 服务器部署步骤

### 1️⃣ 更新代码

```bash
# SSH 登录
ssh acs@app7626.acapp.acwing.com.cn

# 进入项目目录
cd ~/kotlin_calendar

# 拉取最新代码
git pull
```

**预计时间**: < 10 秒

---

### 2️⃣ 更新 Nginx 配置

```bash
# 复制配置文件
sudo cp backend/nginx.conf /etc/nginx/nginx.conf

# 测试配置是否正确
sudo nginx -t

# 应该输出：
# nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
# nginx: configuration file /etc/nginx/nginx.conf test is successful
```

---

### 3️⃣ 重新加载 Nginx

```bash
# 重新加载配置（不中断服务）
sudo nginx -s reload

# 或重启 Nginx
sudo systemctl restart nginx
```

---

### 4️⃣ 验证部署

```bash
# 测试 acapp 文件是否可访问
curl https://app7626.acapp.acwing.com.cn/acapp/app.js -I

# 应该返回：
# HTTP/2 200
# content-type: application/javascript
```

---

## 🎯 AcWing 平台配置

### 访问 AcWing 管理后台

1. 访问 https://www.acwing.com/
2. 进入应用管理 → kotlin_calendar
3. 配置文件地址：

| 配置项 | 值 |
|--------|-----|
| **CSS 地址** | `https://app7626.acapp.acwing.com.cn/acapp/app.css` |
| **JS 地址** | `https://app7626.acapp.acwing.com.cn/acapp/app.js` |
| **主类名** | `Calendar` |

---

## 🧪 测试访问

### 浏览器测试

```bash
# Web 端
https://app7626.acapp.acwing.com.cn/

# AcWing 端（直接访问）
https://app7626.acapp.acwing.com.cn/acapp/

# JS 文件
https://app7626.acapp.acwing.com.cn/acapp/app.js

# CSS 文件
https://app7626.acapp.acwing.com.cn/acapp/app.css
```

### API 测试

```bash
# 测试 API 是否正常
curl https://app7626.acapp.acwing.com.cn/api/events/
```

---

## 🔄 后续更新流程

### 本地修改代码

```bash
cd acapp_frontend

# 修改代码
# ...

# 构建
npm run build

# 输出到 ../acapp/dist/
```

### 提交到 Git

```bash
git add acapp/dist/
git commit -m "build: update acapp"
git push
```

### 服务器更新

```bash
# SSH 登录服务器
ssh acs@app7626.acapp.acwing.com.cn

# 拉取最新代码
cd ~/kotlin_calendar
git pull

# 无需重启（Nginx 自动提供最新文件）
```

---

## ⚠️ 注意事项

### 1. CORS 配置

Nginx 已添加 CORS 头：

```nginx
add_header Access-Control-Allow-Origin *;
```

允许 AcWing 平台跨域加载文件。

### 2. 缓存配置

```nginx
add_header Cache-Control "no-cache";
```

确保 AcWing 平台总是获取最新版本。

### 3. 文件权限

```bash
# 确保文件可读
chmod 644 ~/kotlin_calendar/acapp/dist/*
```

---

## 🐛 常见问题

### Q1: 404 Not Found

```bash
# 检查文件是否存在
ls ~/kotlin_calendar/acapp/dist/

# 应该有：
# app.js  app.css  index.html  favicon.ico
```

### Q2: 403 Forbidden

```bash
# 检查权限
ls -la ~/kotlin_calendar/acapp/dist/

# 修复权限
chmod 755 ~/kotlin_calendar/acapp/dist/
chmod 644 ~/kotlin_calendar/acapp/dist/*
```

### Q3: Nginx 配置错误

```bash
# 测试配置
sudo nginx -t

# 查看错误日志
sudo tail -f /var/log/nginx/error.log
```

### Q4: CORS 错误

检查 Nginx 配置中是否包含：

```nginx
add_header Access-Control-Allow-Origin *;
```

---

## 📊 部署验证清单

- [ ] `git pull` 成功
- [ ] `acapp/dist/` 目录存在
- [ ] `app.js` 和 `app.css` 文件存在
- [ ] Nginx 配置更新
- [ ] `sudo nginx -t` 通过
- [ ] `sudo nginx -s reload` 成功
- [ ] 浏览器访问 `/acapp/` 正常
- [ ] JS/CSS 文件可下载
- [ ] AcWing 平台配置完成

---

## 🎉 部署完成！

现在你有**三个客户端**运行在同一个域名下：

- **Web 端**: https://app7626.acapp.acwing.com.cn/
- **AcWing 端**: https://app7626.acapp.acwing.com.cn/acapp/
- **API**: https://app7626.acapp.acwing.com.cn/api/
- **Android 端**: 手机 APK（连接同一个 API）

**完美的三客户端架构！** 🚀


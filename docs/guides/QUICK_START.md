# 🚀 Ralendar 快速启动指南

## Docker 启动命令（推荐）

如果项目已经Docker化，使用以下命令：

### 启动所有服务

```bash
cd ~/ralendar  # 或你的项目目录
docker-compose up -d
```

### 查看服务状态

```bash
docker-compose ps
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f web
docker-compose logs -f celery
docker-compose logs -f db
docker-compose logs -f redis
```

### 停止服务

```bash
docker-compose stop
```

### 重启服务

```bash
docker-compose restart

# 重启特定服务
docker-compose restart web
docker-compose restart celery
```

### 停止并删除容器

```bash
docker-compose down
```

### 重新构建并启动

```bash
docker-compose up -d --build
```

---

## 传统部署启动命令

如果使用传统部署方式（uWSGI/Gunicorn + Nginx）：

### 启动后端服务

```bash
cd ~/ralendar/backend

# 方式1: 使用systemd（推荐）
sudo systemctl start gunicorn
# 或
sudo systemctl start uwsgi

# 方式2: 手动启动
source venv/bin/activate
gunicorn calendar_backend.wsgi:application --bind 0.0.0.0:8000
# 或
uwsgi --ini uwsgi.ini
```

### 启动Celery（邮件提醒）

```bash
cd ~/ralendar/backend

# 方式1: 使用脚本
./start_celery.sh

# 方式2: 手动启动（需要两个终端）
# 终端1: Worker
celery -A calendar_backend worker --loglevel=info

# 终端2: Beat（定时任务）
celery -A calendar_backend beat --loglevel=info
```

### 启动Nginx

```bash
sudo systemctl start nginx
# 或
sudo nginx
```

---

## 验证服务

### 检查API是否正常

```bash
curl http://localhost:8000/api/v1/health/
# 或
curl https://app7626.acapp.acwing.com.cn/api/v1/health/
```

### 检查前端是否正常

```bash
curl http://localhost/
# 或
curl https://app7626.acapp.acwing.com.cn/
```

### 检查数据库连接

```bash
# Docker方式
docker exec ralendar-web python manage.py check --database default

# 传统方式
cd ~/ralendar/backend
python manage.py check --database default
```

---

## 常用管理命令

### Docker方式

```bash
# 进入容器
docker exec -it ralendar-web bash

# 执行Django命令
docker exec ralendar-web python manage.py migrate
docker exec ralendar-web python manage.py collectstatic --noinput
docker exec ralendar-web python manage.py createsuperuser

# 查看容器资源使用
docker stats
```

### 传统方式

```bash
cd ~/ralendar/backend
source venv/bin/activate

# 数据库迁移
python manage.py migrate

# 收集静态文件
python manage.py collectstatic --noinput

# 创建超级用户
python manage.py createsuperuser

# 查看进程
ps aux | grep gunicorn
ps aux | grep celery
```

---

## 故障排查

### 服务无法启动

```bash
# Docker方式
docker-compose logs web
docker-compose logs celery

# 传统方式
sudo systemctl status gunicorn
sudo systemctl status celery
tail -f /var/log/gunicorn/error.log
```

### 端口被占用

```bash
# 查看端口占用
netstat -tlnp | grep 8000
# 或
lsof -i :8000
```

### 数据库连接失败

```bash
# 检查数据库容器/服务是否运行
docker-compose ps db
# 或
sudo systemctl status mysql

# 测试连接
docker exec ralendar-web python manage.py dbshell
```

---

**最后更新**: 2025年11月13日


# 🔧 uWSGI 启动和管理命令

## 📋 启动前准备

### 1. 创建日志目录

```bash
cd ~/ralendar/backend
mkdir -p logs
```

### 2. 检查配置文件

确保 `uwsgi.ini` 中的路径正确：
- `chdir` = `/home/acs/ralendar/backend`
- `logto` = `/home/acs/ralendar/backend/logs/uwsgi.log`
- `pidfile` = `/home/acs/ralendar/backend/uwsgi.pid`

---

## 🚀 启动命令

### 方式1: 使用配置文件（推荐）

```bash
cd ~/ralendar/backend
uwsgi --ini uwsgi.ini
```

### 方式2: 前台运行（调试用）

```bash
cd ~/ralendar/backend
uwsgi --ini uwsgi.ini --daemonize /dev/null
```

### 方式3: 命令行参数

```bash
cd ~/ralendar/backend
uwsgi \
    --chdir /home/acs/ralendar/backend \
    --module calendar_backend.wsgi:application \
    --socket 127.0.0.1:8000 \
    --master \
    --processes 2 \
    --threads 5 \
    --daemonize /home/acs/ralendar/backend/logs/uwsgi.log \
    --pidfile /home/acs/ralendar/backend/uwsgi.pid
```

---

## 🛑 停止命令

### 方式1: 使用PID文件（推荐）

```bash
cd ~/ralendar/backend
uwsgi --stop uwsgi.pid
```

### 方式2: 使用进程名

```bash
sudo pkill -9 uwsgi
# 或
pkill -f uwsgi
```

### 方式3: 查找并杀死进程

```bash
# 查找uwsgi进程
ps aux | grep uwsgi

# 杀死进程（替换PID为实际进程ID）
kill -9 <PID>
```

---

## 🔄 重启命令

### 方式1: 优雅重启（推荐）

```bash
cd ~/ralendar/backend
uwsgi --reload uwsgi.pid
```

### 方式2: 停止后启动

```bash
cd ~/ralendar/backend
uwsgi --stop uwsgi.pid
sleep 2
uwsgi --ini uwsgi.ini
```

---

## 📊 查看状态

### 检查进程

```bash
ps aux | grep uwsgi
```

### 检查端口

```bash
netstat -tlnp | grep 8000
# 或
lsof -i :8000
```

### 查看日志

```bash
tail -f ~/ralendar/backend/logs/uwsgi.log
```

### 查看PID文件

```bash
cat ~/ralendar/backend/uwsgi.pid
```

---

## 🔍 测试uWSGI

### 测试配置

```bash
cd ~/ralendar/backend
uwsgi --ini uwsgi.ini --check-static /home/acs/ralendar/backend
```

### 测试HTTP连接

```bash
curl http://127.0.0.1:8000/api/v1/health/
```

---

## ⚙️ 使用systemd管理（推荐生产环境）

### 创建systemd服务文件

```bash
sudo nano /etc/systemd/system/ralendar-uwsgi.service
```

内容：

```ini
[Unit]
Description=uWSGI instance to serve Ralendar
After=network.target

[Service]
User=acs
Group=acs
WorkingDirectory=/home/acs/ralendar/backend
Environment="PATH=/home/acs/ralendar/backend/venv/bin"
ExecStart=/home/acs/ralendar/backend/venv/bin/uwsgi --ini /home/acs/ralendar/backend/uwsgi.ini
Restart=always
KillSignal=SIGQUIT
Type=notify
StandardError=syslog
NotifyAccess=all

[Install]
WantedBy=multi-user.target
```

### 使用systemd命令

```bash
# 启动
sudo systemctl start ralendar-uwsgi

# 停止
sudo systemctl stop ralendar-uwsgi

# 重启
sudo systemctl restart ralendar-uwsgi

# 查看状态
sudo systemctl status ralendar-uwsgi

# 开机自启
sudo systemctl enable ralendar-uwsgi

# 查看日志
sudo journalctl -u ralendar-uwsgi -f
```

---

## 🐛 常见问题

### 问题1: 日志文件路径不存在

**错误**:
```
open("/home/acs/kotlin_calendar/backend/logs/uwsgi.log"): No such file or directory
```

**解决**:
```bash
# 1. 创建logs目录
mkdir -p ~/ralendar/backend/logs

# 2. 检查uwsgi.ini中的路径是否正确
# 确保所有路径都指向 /home/acs/ralendar/backend
```

### 问题2: PID文件已存在

**错误**:
```
uwsgi: another instance of uWSGI is running on the same address (pid=xxx)
```

**解决**:
```bash
# 1. 停止旧进程
uwsgi --stop uwsgi.pid

# 2. 如果停止失败，强制杀死
pkill -9 uwsgi

# 3. 删除PID文件
rm -f ~/ralendar/backend/uwsgi.pid

# 4. 重新启动
uwsgi --ini uwsgi.ini
```

### 问题3: 端口被占用

**错误**:
```
bind(): Address already in use [core/socket.c line 769]
```

**解决**:
```bash
# 1. 查找占用8000端口的进程
lsof -i :8000

# 2. 停止占用端口的进程
kill -9 <PID>

# 3. 或修改uwsgi.ini中的端口
# socket = 127.0.0.1:8001
```

### 问题4: 权限错误

**错误**:
```
permission denied
```

**解决**:
```bash
# 确保用户有权限访问项目目录
chown -R acs:acs ~/ralendar

# 确保日志目录可写
chmod 755 ~/ralendar/backend/logs
```

---

## 📝 完整启动流程

```bash
# 1. 进入项目目录
cd ~/ralendar/backend

# 2. 创建日志目录
mkdir -p logs

# 3. 激活虚拟环境（如果使用）
source venv/bin/activate

# 4. 检查配置
cat uwsgi.ini | grep -E "chdir|logto|pidfile"

# 5. 停止旧进程（如果有）
uwsgi --stop uwsgi.pid 2>/dev/null || pkill -9 uwsgi

# 6. 启动uWSGI
uwsgi --ini uwsgi.ini

# 7. 检查状态
ps aux | grep uwsgi
tail -f logs/uwsgi.log
```

---

**最后更新**: 2025年11月13日


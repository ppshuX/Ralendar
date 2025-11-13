<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-gradient">
    <div class="container-fluid">
      <!-- Logo -->
      <router-link to="/calendar" class="navbar-brand">
        <img src="/logo.png" alt="Ralendar" class="brand-logo" />
        <span class="brand-text">Ralendar</span>
      </router-link>
      
      <!-- 移动端折叠按钮 -->
      <button 
        class="navbar-toggler" 
        type="button" 
        data-bs-toggle="collapse" 
        data-bs-target="#navbarNav"
      >
        <span class="navbar-toggler-icon"></span>
      </button>
      
      <!-- 导航菜单 -->
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ms-auto align-items-center">
          <!-- 用户工具区 -->
          <li class="nav-item">
            <div class="nav-tools-card">
              <!-- 未登录状态 -->
              <template v-if="!currentUser">
                <router-link to="/login" class="nav-link nav-link-btn">
                  <i class="bi bi-box-arrow-in-right"></i> 登录
                </router-link>
              </template>
              
              <!-- 已登录状态 -->
              <div v-else class="dropdown">
              <a 
                class="nav-link dropdown-toggle user-link" 
                href="#" 
                id="userDropdown" 
                role="button" 
                data-bs-toggle="dropdown"
              >
                <img 
                  v-if="currentUser.photo" 
                  :src="currentUser.photo" 
                  alt="头像" 
                  class="user-avatar"
                />
                <i v-else class="bi bi-person-circle"></i>
                <span class="user-name-text">{{ currentUser.username }}</span>
              </a>
              <ul class="dropdown-menu dropdown-menu-end">
                <li class="dropdown-item-text">
                  <div class="user-info">
                    <div class="user-name">{{ currentUser.username }}</div>
                    <div class="user-email">{{ currentUser.email || '未设置邮箱' }}</div>
                  </div>
                </li>
                <li><hr class="dropdown-divider"></li>
                <li>
                  <router-link to="/profile" class="dropdown-item">
                    <i class="bi bi-person-circle"></i> 个人中心
                  </router-link>
                </li>
                <li><hr class="dropdown-divider"></li>
                <li><a class="dropdown-item" href="#" @click.prevent="handleLogout">
                  <i class="bi bi-box-arrow-right"></i> 退出登录
                </a></li>
              </ul>
              </div>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { authAPI } from '../api'

const router = useRouter()
const currentUser = ref(null)

// 获取当前用户信息
const fetchCurrentUser = async () => {
  const token = localStorage.getItem('access_token')
  if (!token) {
    currentUser.value = null
    return
  }
  
  // 添加小延迟确保 axios 拦截器已设置
  await new Promise(resolve => setTimeout(resolve, 50))
  
  try {
    const user = await authAPI.getCurrentUser()
    currentUser.value = user
  } catch (error) {
    // 未登录或 token 过期，静默失败
    currentUser.value = null
  }
}

// 退出登录
const handleLogout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  currentUser.value = null
  ElMessage.success('已退出登录')
  router.push('/login')
}

onMounted(async () => {
  await fetchCurrentUser()
})

// 暴露方法供父组件调用
defineExpose({
  fetchCurrentUser
})
</script>

<style scoped>
/* navbar 样式已在 .dropdown-menu 上面定义，避免重复 */

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  font-size: 24px;
}

.brand-logo {
  width: 32px;
  height: 32px;
  object-fit: contain;
  filter: brightness(0) invert(1);
  transition: transform 0.3s;
}

.brand-logo:hover {
  transform: scale(1.1) rotate(5deg);
}

.brand-text {
  background: linear-gradient(135deg, #fff, #f0f0f0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.nav-link {
  color: rgba(255, 255, 255, 0.9) !important;
  font-weight: 500;
  padding: 8px 16px !important;
  border-radius: 8px;
  transition: all 0.3s;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff !important;
  transform: translateY(-2px);
}

.dropdown-menu {
  border-radius: 12px;
  border: none;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  padding: 8px;
  z-index: 1050 !important;  /* Bootstrap dropdown 标准 z-index */
  position: absolute !important;
}

/* 确保 navbar 本身也有合适的 z-index */
.navbar {
  background: linear-gradient(135deg, #667eea, #764ba2) !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 12px 0;
  position: relative;
  z-index: 1040;  /* 确保 navbar 在主内容之上 */
}

.dropdown-item {
  border-radius: 8px;
  padding: 10px 16px;
  transition: all 0.2s;
}

.dropdown-item:hover {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  transform: translateX(4px);
}

.dropdown-item-text {
  padding: 8px 16px;
}

.user-info {
  padding: 4px 0;
}

.user-name {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.user-email {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.user-link {
  display: flex !important;
  align-items: center;
  gap: 8px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid rgba(255, 255, 255, 0.8);
}

.user-name-text {
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 工具卡片样式 */
.nav-tools-card {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  padding: 6px 12px;
  border-radius: 30px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.nav-tools-card:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
}

.nav-link-btn {
  color: rgba(255, 255, 255, 0.95) !important;
  font-weight: 500;
  padding: 6px 12px !important;
  border-radius: 20px;
  transition: all 0.3s;
  text-decoration: none;
  white-space: nowrap;
}

.nav-link-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #fff !important;
}

.nav-tools-card .user-link {
  padding: 6px 12px !important;
}

/* 移动端优化 */
@media (max-width: 768px) {
  .navbar {
    padding: 8px 0;
  }
  
  .navbar-brand {
    font-size: 18px;
    gap: 6px;
  }
  
  .brand-logo {
    width: 24px;
    height: 24px;
  }
  
  .nav-link {
    padding: 6px 12px !important;
    font-size: 14px;
  }
  
  .user-avatar {
    width: 28px;
    height: 28px;
  }
  
  .user-name-text {
    max-width: 80px;
    font-size: 13px;
  }
}

@media (max-width: 576px) {
  .navbar {
    padding: 8px 0;
  }
  
  .container-fluid {
    padding-left: 12px;
    padding-right: 12px;
  }
  
  .navbar-brand {
    font-size: 18px;
    gap: 6px;
  }
  
  .brand-logo {
    width: 24px;
    height: 24px;
  }
  
  .brand-text {
    font-size: 18px;
  }
  
  .navbar-nav {
    gap: 4px;
  }
  
  .nav-link {
    padding: 6px 10px !important;
    font-size: 14px;
  }
  
  .nav-link i {
    font-size: 16px;
  }
  
  .user-avatar {
    width: 28px;
    height: 28px;
    border-width: 1.5px;
  }
  
  .user-name-text {
    display: none;
  }
  
  .dropdown-menu {
    min-width: 220px;
    right: 0 !important;
    left: auto !important;
  }
  
  .dropdown-item {
    padding: 12px 16px;
    font-size: 15px;
  }
  
  .user-name {
    font-size: 15px;
  }
  
  .user-email {
    font-size: 13px;
  }
}
</style>


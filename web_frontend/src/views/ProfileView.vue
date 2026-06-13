<template>
  <div class="profile-page">
    <div class="profile-container">
      <div class="profile-card">
        <h2 class="profile-title">个人中心</h2>
        <div v-if="user" class="user-info">
          <div class="avatar-section">
            <img v-if="user.photo" :src="user.photo" alt="头像" class="avatar" />
            <div v-else class="avatar-placeholder">
              <i class="bi bi-person-circle"></i>
            </div>
          </div>
          <div class="info-list">
            <div class="info-item">
              <span class="label">用户名</span>
              <span class="value">{{ user.username }}</span>
            </div>
            <div class="info-item">
              <span class="label">邮箱</span>
              <span class="value">{{ user.email || '未设置' }}</span>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <p>请先登录</p>
          <router-link to="/login" class="login-link">去登录</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI } from '../api'

const router = useRouter()
const user = ref(null)

onMounted(async () => {
  const token = localStorage.getItem('access_token')
  if (!token) {
    router.push('/login')
    return
  }

  try {
    user.value = await authAPI.getCurrentUser()
  } catch (error) {
    router.push('/login')
  }
})
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 40px 20px;
}

.profile-container {
  max-width: 600px;
  margin: 0 auto;
}

.profile-card {
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.profile-title {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 30px;
}

.avatar-section {
  text-align: center;
  margin-bottom: 30px;
}

.avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid #667eea;
}

.avatar-placeholder {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}

.avatar-placeholder i {
  font-size: 60px;
  color: #c0c4cc;
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-item .label {
  color: #909399;
  font-size: 14px;
}

.info-item .value {
  color: #303133;
  font-weight: 500;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
  color: #909399;
}

.login-link {
  display: inline-block;
  margin-top: 16px;
  padding: 8px 24px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
}
</style>

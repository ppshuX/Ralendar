# AI智能助手规划

## 🎯 产品愿景
打造一个"会说话"的智能日历，用户只需说出需求，AI自动完成日程管理。

---

## 🌟 核心功能

### 1. 语音创建日程
**场景**：用户开车时
```
用户: "明天下午3点提醒我开会"
AI: "好的，已为您创建明天15:00的会议提醒"
```

### 2. 智能理解时间
**自然语言处理**：
- "明天" → 2025-11-07
- "下周五" → 2025-11-15
- "三天后" → 2025-11-09
- "下个月1号" → 2025-12-01

### 3. 智能补全信息
```
用户: "明天和小王吃饭"
AI: "已创建：
    时间：明天19:00（默认晚餐时间）
    时长：1小时
    提醒：提前1小时
    需要预定餐厅吗？"
```

### 4. 日程管理对话
```
用户: "我明天有什么安排？"
AI: "明天有3个日程：
    1. 09:00 团队会议
    2. 15:00 客户拜访
    3. 19:00 与小王聚餐"

用户: "把会议改到下午4点"
AI: "已将团队会议调整到明天16:00"
```

---

## 🚀 技术实现

### 架构图
```
前端（Vue3/acapp）
    ↓ WebSocket/HTTP
Django Backend
    ↓ API调用
OpenAI GPT-4 / 通义千问
    ↓ 结构化输出
Event Creation
    ↓ Celery定时
推送通知
```

### 核心技术栈
1. **NLP引擎**：OpenAI GPT-4 Turbo
2. **语音识别**：讯飞语音 / 腾讯云ASR
3. **语音合成**：讯飞TTS（可选）
4. **定时任务**：Celery + Redis
5. **消息推送**：
   - Web: Service Worker Push
   - 微信: 公众号模板消息
   - 邮件: Django Email

---

## 📋 API设计

### 1. AI对话接口
```python
POST /api/ai/chat/
Request:
{
    "message": "明天下午3点提醒我开会",
    "context": {  # 可选，上下文
        "last_event_id": 123
    }
}

Response:
{
    "ai_reply": "好的，已为您创建会议提醒",
    "action": {
        "type": "create_event",
        "data": {
            "title": "会议",
            "start_time": "2025-11-07T15:00:00",
            "end_time": "2025-11-07T16:00:00",
            "reminder_minutes": 15
        }
    },
    "event": {
        "id": 456,
        "title": "会议",
        ...
    }
}
```

### 2. 语音转文本
```python
POST /api/ai/speech-to-text/
Request: FormData
{
    "audio": <binary_audio_file>
}

Response:
{
    "text": "明天下午3点提醒我开会",
    "confidence": 0.98
}
```

### 3. 智能提醒配置
```python
POST /api/events/{id}/reminder/
{
    "reminder_type": "push",  # push/email/sms/wechat
    "before_minutes": 15
}
```

---

## 🎨 前端实现

### Vue3组件设计
```vue
<!-- AIAssistant.vue -->
<template>
  <div class="ai-assistant">
    <!-- 悬浮按钮 -->
    <button class="ai-fab" @click="toggleChat">
      <span v-if="listening">🎙️</span>
      <span v-else>🤖</span>
    </button>
    
    <!-- 对话窗口 -->
    <transition name="slide-up">
      <div v-if="showChat" class="chat-window">
        <!-- 消息列表 -->
        <div class="messages">
          <div 
            v-for="msg in messages" 
            :key="msg.id"
            :class="['message', msg.role]"
          >
            <div class="avatar">{{ msg.role === 'user' ? '👤' : '🤖' }}</div>
            <div class="content">{{ msg.content }}</div>
          </div>
        </div>
        
        <!-- 输入区 -->
        <div class="input-area">
          <button 
            @click="toggleVoice"
            :class="{ recording: listening }"
          >
            {{ listening ? '🔴' : '🎤' }}
          </button>
          
          <input 
            v-model="userInput"
            @keyup.enter="sendMessage"
            placeholder="试试说：明天下午3点提醒我开会"
          />
          
          <button @click="sendMessage">发送</button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const showChat = ref(false)
const messages = ref([])
const userInput = ref('')
const listening = ref(false)

// 发送消息
const sendMessage = async () => {
  if (!userInput.value.trim()) return
  
  // 添加用户消息
  messages.value.push({
    id: Date.now(),
    role: 'user',
    content: userInput.value
  })
  
  const userMsg = userInput.value
  userInput.value = ''
  
  // 调用AI API
  try {
    const { data } = await axios.post('/api/ai/chat/', {
      message: userMsg
    })
    
    // 添加AI回复
    messages.value.push({
      id: Date.now() + 1,
      role: 'assistant',
      content: data.ai_reply
    })
    
    // 如果有动作，执行
    if (data.action) {
      executeAction(data.action)
    }
  } catch (error) {
    console.error('AI对话失败:', error)
  }
}

// 执行AI动作
const executeAction = (action) => {
  if (action.type === 'create_event') {
    // 刷新日历
    window.location.reload()  // 或者调用Vuex action
  }
}

// 语音识别
const toggleVoice = () => {
  if (!listening.value) {
    startVoiceRecognition()
  } else {
    stopVoiceRecognition()
  }
}
</script>

<style scoped>
.ai-fab {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 24px;
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  transition: all 0.3s;
}

.ai-fab:hover {
  transform: scale(1.1);
}

.chat-window {
  position: fixed;
  bottom: 100px;
  right: 20px;
  width: 350px;
  height: 500px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 15px;
}

.message {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.message.user {
  flex-direction: row-reverse;
}

.message .content {
  background: #f0f0f0;
  padding: 10px 15px;
  border-radius: 12px;
  max-width: 70%;
}

.message.user .content {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.input-area {
  display: flex;
  gap: 8px;
  padding: 15px;
  border-top: 1px solid #eee;
}

button.recording {
  background: #f56c6c;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}
</style>
```

---

## 💰 商业化策略

### VIP会员权益
| 功能 | 免费用户 | VIP会员 |
|------|---------|---------|
| AI对话次数 | 10次/天 | 无限制 |
| 语音输入 | ❌ | ✅ |
| 智能提醒 | 仅邮件 | 多渠道（微信/短信/邮件） |
| 语音播报 | ❌ | ✅ |
| 日程分析 | ❌ | ✅ AI生成日报/周报 |
| 习惯建议 | ❌ | ✅ 个性化时间管理建议 |

### 定价策略
- **月卡**: ¥9.9/月
- **年卡**: ¥88/年（省30%）
- **终身卡**: ¥299（限时优惠）

---

## 🎯 MVP开发计划（2周）

### Week 1: 后端AI接口
- [ ] 集成OpenAI API
- [ ] 时间解析逻辑
- [ ] Event自动创建
- [ ] API接口开发

### Week 2: 前端UI
- [ ] AI对话组件
- [ ] 语音录音功能
- [ ] 消息展示
- [ ] 与日历集成

---

## 🔮 未来扩展

1. **多语言支持**：英文、日文、韩文
2. **情感识别**：根据语气调整提醒强度
3. **主动建议**："您明天9点有会，现在出发可能会迟到"
4. **团队协作**："帮我约小王明天有空的时间"
5. **习惯学习**：自动识别用户偏好

---

## 🏆 竞争优势

市面上的AI日历App对比：

| 产品 | AI能力 | 语音 | 提醒 | 价格 |
|------|--------|------|------|------|
| Google Calendar | ❌ | ❌ | ✅ | 免费 |
| Notion Calendar | ⚠️ 有限 | ❌ | ✅ | $10/月 |
| **KotlinCalendar** | ✅ 完整 | ✅ | ✅ | ¥9.9/月 |

**我们的优势**：
- ✅ 中文AI理解更准确
- ✅ 价格更亲民
- ✅ 三端同步（Android/Web/AcWing）
- ✅ 本土化功能（节假日/农历）

---

## 📞 技术支持方案

### 客服AI助手
```
用户: "怎么用AI创建日程？"
AI: "很简单！点击右下角的🤖按钮，
    然后说：'明天下午3点提醒我开会'
    我就会自动帮您创建了😊"
```

---

**这是一个非常有前景的方向！我强烈建议先做一个文本AI助手的MVP，验证用户需求后再加语音功能。**

**需要我帮你开始实现吗？** 🚀


# Day 10 开发日志 - Android 网络功能集成

**日期**：____年____月____日

---

## 今天做了什么

- [ ] 添加 Retrofit 依赖
- [ ] 创建 API 接口定义
- [ ] 实现网络日历订阅功能
- [ ] 实现农历显示
- [ ] 实现云端备份/恢复（可选）
- [ ] 测试联调

---

## 写了哪些代码

### 1. 添加依赖

```kotlin
// app/build.gradle.kts
dependencies {
    // Retrofit 网络库
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-gson:2.9.0")
    
    // OkHttp (日志拦截器)
    implementation("com.squareup.okhttp3:logging-interceptor:4.11.0")
}
```

---

### 2. API 接口定义

```kotlin
// api/CalendarApi.kt
package com.ncu.kotlincalendar.api

import retrofit2.http.*

data class EventResponse(
    val id: Long,
    val title: String,
    val description: String,
    val date_time: String,
    val reminder_minutes: Int
)

data class LunarResponse(
    val lunar_date: String,
    val year: Int,
    val month: String,
    val day: String,
    val zodiac: String
)

interface CalendarApi {
    
    @GET("events/")
    suspend fun getEvents(): List<EventResponse>
    
    @POST("events/")
    suspend fun createEvent(@Body event: EventResponse): EventResponse
    
    @PUT("events/{id}/")
    suspend fun updateEvent(@Path("id") id: Long, @Body event: EventResponse): EventResponse
    
    @DELETE("events/{id}/")
    suspend fun deleteEvent(@Path("id") id: Long)
    
    @GET("calendars/{slug}/feed/")
    suspend fun getCalendarFeed(@Path("slug") slug: String): String
    
    @GET("lunar/")
    suspend fun getLunarDate(@Query("date") date: String): LunarResponse
}
```

---

### 3. Retrofit 配置

```kotlin
// api/RetrofitClient.kt
package com.ncu.kotlincalendar.api

import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object RetrofitClient {
    
    private const val BASE_URL = "https://your-server.com/api/"
    
    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    }
    
    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(loggingInterceptor)
        .build()
    
    val api: CalendarApi by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(CalendarApi::class.java)
    }
}
```

---

### 4. 订阅网络日历功能

```kotlin
// MainActivity.kt

// 在布局中添加订阅按钮
<com.google.android.material.button.MaterialButton
    android:id="@+id/btnSubscribe"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_margin="16dp"
    android:text="📡 订阅网络日历"
    app:cornerRadius="12dp" />

// 实现订阅功能
private fun setupSubscribeButton() {
    btnSubscribe.setOnClickListener {
        showSubscribeDialog()
    }
}

private fun showSubscribeDialog() {
    val options = arrayOf("中国法定节假日", "农历节气", "国际纪念日")
    val slugs = arrayOf("china-holidays", "lunar-festivals", "world-days")
    
    AlertDialog.Builder(this)
        .setTitle("📡 选择订阅日历")
        .setItems(options) { _, which ->
            subscribeCalendar(slugs[which])
        }
        .show()
}

private fun subscribeCalendar(slug: String) {
    lifecycleScope.launch {
        try {
            // 显示加载提示
            Toast.makeText(this@MainActivity, "⏳ 正在订阅...", Toast.LENGTH_SHORT).show()
            
            // 获取日历订阅内容
            val icsContent = withContext(Dispatchers.IO) {
                RetrofitClient.api.getCalendarFeed(slug)
            }
            
            // 解析 iCalendar 格式
            val events = parseICS(icsContent)
            
            // 保存到本地数据库
            withContext(Dispatchers.IO) {
                events.forEach { event ->
                    eventDao.insert(event)
                }
            }
            
            // 刷新列表
            loadAllEvents()
            
            Toast.makeText(this@MainActivity, "✅ 订阅成功！已添加 ${events.size} 个日程", Toast.LENGTH_SHORT).show()
        } catch (e: Exception) {
            Toast.makeText(this@MainActivity, "❌ 订阅失败: ${e.message}", Toast.LENGTH_SHORT).show()
        }
    }
}

private fun parseICS(icsContent: String): List<Event> {
    // TODO: 实现 iCalendar 解析
    // 可以使用 ical4j 库
    return emptyList()
}
```

---

### 5. 农历显示功能

```kotlin
// 在日程卡片中添加农历
private fun showLunarDate(dateTime: Long) {
    lifecycleScope.launch {
        try {
            val dateFormat = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
            val dateStr = dateFormat.format(Date(dateTime))
            
            val lunar = withContext(Dispatchers.IO) {
                RetrofitClient.api.getLunarDate(dateStr)
            }
            
            // 显示农历
            tvLunar.text = "🏮 ${lunar.lunar_date} ${lunar.zodiac}年"
            tvLunar.visibility = View.VISIBLE
        } catch (e: Exception) {
            // 失败就不显示
            tvLunar.visibility = View.GONE
        }
    }
}

// 在 item_event.xml 中添加农历显示
<TextView
    android:id="@+id/tvLunar"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="4dp"
    android:textSize="12sp"
    android:textColor="@android:color/holo_red_light"
    android:visibility="gone"
    tools:text="🏮 农历十月初五 蛇年" />
```

---

### 6. 云端备份/恢复（可选）

```kotlin
// 备份到云端
private fun backupToCloud() {
    lifecycleScope.launch {
        try {
            Toast.makeText(this@MainActivity, "⏳ 正在备份...", Toast.LENGTH_SHORT).show()
            
            val localEvents = withContext(Dispatchers.IO) {
                eventDao.getAllEvents()
            }
            
            // 上传到云端
            withContext(Dispatchers.IO) {
                localEvents.forEach { event ->
                    val response = EventResponse(
                        id = 0,  // 服务器会自动生成
                        title = event.title,
                        description = event.description,
                        date_time = formatDateTime(event.dateTime),
                        reminder_minutes = event.reminderMinutes
                    )
                    RetrofitClient.api.createEvent(response)
                }
            }
            
            Toast.makeText(this@MainActivity, "✅ 备份成功！", Toast.LENGTH_SHORT).show()
        } catch (e: Exception) {
            Toast.makeText(this@MainActivity, "❌ 备份失败: ${e.message}", Toast.LENGTH_SHORT).show()
        }
    }
}

// 从云端恢复
private fun restoreFromCloud() {
    lifecycleScope.launch {
        try {
            Toast.makeText(this@MainActivity, "⏳ 正在恢复...", Toast.LENGTH_SHORT).show()
            
            val cloudEvents = withContext(Dispatchers.IO) {
                RetrofitClient.api.getEvents()
            }
            
            // 保存到本地
            withContext(Dispatchers.IO) {
                cloudEvents.forEach { response ->
                    val event = Event(
                        title = response.title,
                        description = response.description,
                        dateTime = parseDateTime(response.date_time),
                        reminderMinutes = response.reminder_minutes
                    )
                    eventDao.insert(event)
                }
            }
            
            loadAllEvents()
            Toast.makeText(this@MainActivity, "✅ 恢复成功！", Toast.LENGTH_SHORT).show()
        } catch (e: Exception) {
            Toast.makeText(this@MainActivity, "❌ 恢复失败: ${e.message}", Toast.LENGTH_SHORT).show()
        }
    }
}
```

---

## 测试结果

- [ ] 网络日历订阅成功
- [ ] 农历显示正常
- [ ] 云端备份/恢复成功
- [ ] 错误处理正常

---

## 遇到的坑

**问题**：


**怎么解决的**：


---

**今天状态**：😊 顺利 / 😐 一般 / 😓 卡了好久


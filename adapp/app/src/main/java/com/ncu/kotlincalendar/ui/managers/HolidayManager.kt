package com.ncu.kotlincalendar.ui.managers

import android.content.Context
import android.content.Intent
import android.view.View
import android.widget.LinearLayout
import android.widget.TextView
import androidx.lifecycle.LifecycleCoroutineScope
import com.google.android.material.card.MaterialCardView
import com.ncu.kotlincalendar.FestivalDetailActivity
import com.ncu.kotlincalendar.api.client.RetrofitClient
import com.ncu.kotlincalendar.data.managers.SubscriptionManager
import com.ncu.kotlincalendar.data.managers.FestivalSubscriptionManager
import com.ncu.kotlincalendar.data.models.Event
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.text.SimpleDateFormat
import java.time.Instant
import java.time.LocalDate
import java.time.ZoneId
import java.util.*

/**
 * 节日信息管理器
 * 
 * 职责：
 * - 加载节日信息（API + 订阅）
 * - 动态创建节日卡片
 * - 处理节日卡片点击事件
 * 
 * 使用方式：
 * ```kotlin
 * val holidayManager = HolidayManager(festivalCardsContainer, tvHolidayHint, context, subscriptionManager)
 * holidayManager.loadHolidayInfo(dateMillis, lifecycleScope)
 * ```
 */
class HolidayManager(
    private val festivalCardsContainer: LinearLayout,
    private val tvHolidayHint: TextView,
    private val context: Context,
    private val subscriptionManager: SubscriptionManager
) {
    
    // 节日订阅管理器
    private val festivalSubscriptionManager = FestivalSubscriptionManager(context)
    
    /**
     * 加载节日信息
     */
    fun loadHolidayInfo(
        date: Long,
        lifecycleScope: LifecycleCoroutineScope
    ) {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val dateFormat = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
                val dateStr = dateFormat.format(Date(date))
                
                // 1. 调用后端 API 获取节日信息
                val response = RetrofitClient.api.checkHoliday(dateStr)
                
                // 2. 从SubscriptionManager获取该日期的有效订阅节日事件
                // 使用 getVisibleEvents 确保只获取有效且启用的订阅事件
                // 注意：传入date参数会按日期过滤，但为了确保准确性，我们传入null获取所有事件，然后手动过滤
                val selectedDate = Instant.ofEpochMilli(date)
                    .atZone(ZoneId.systemDefault())
                    .toLocalDate()
                
                // 获取所有可见的订阅事件（不过滤日期，因为我们需要检查所有订阅事件）
                val allVisibleEvents = subscriptionManager.getVisibleEvents(null)
                
                // 过滤出该日期的订阅节日事件（subscriptionId != null）
                val subscribedEvents = allVisibleEvents.filter { event ->
                    val eventDate = Instant.ofEpochMilli(event.dateTime)
                        .atZone(ZoneId.systemDefault())
                        .toLocalDate()
                    // 只获取订阅的事件（subscriptionId != null），且日期匹配
                    eventDate == selectedDate && event.subscriptionId != null
                }
                
                withContext(Dispatchers.Main) {
                    // 清空之前的卡片
                    festivalCardsContainer.removeAllViews()
                    
                    // 数据结构：存储节日信息
                    data class FestivalItem(
                        val name: String,
                        val emoji: String,
                        val type: String // "api" 或 "subscribed"
                    )
                    
                    // 合并API节日和订阅节日，并去重
                    val allFestivals = mutableListOf<FestivalItem>()
                    
                    // 添加农历信息卡片（总是显示）
                    addFestivalCard(
                        "🏮 农历",
                        response.lunar ?: "加载中...",
                        "#FFE0B2", // 橙色系 - 农历信息
                        false, // 农历不可点击
                        "", "", ""
                    )
                    
                    // 添加法定节假日卡片
                    if (response.isHoliday) {
                        addFestivalCard(
                            "🎉 法定节假日",
                            "今日为国家法定节假日",
                            "#FFF9C4", // 黄色系 - 法定节假日
                            false, // 法定节假日不可点击
                            "", "", ""
                        )
                    }
                    
                    // 1. 处理API返回的节日列表（方案A：作为默认订阅）
                    if (!response.festivals.isNullOrEmpty()) {
                        // 首次使用时，自动订阅所有API返回的节日
                        if (festivalSubscriptionManager.isFirstInit()) {
                            val festivalNames = response.festivals.map { it.name }
                            festivalSubscriptionManager.subscribeAll(festivalNames)
                            festivalSubscriptionManager.markFirstInitCompleted()
                        }
                        
                        // 只显示已订阅的节日
                        response.festivals.forEach { festival ->
                            if (festivalSubscriptionManager.isSubscribed(festival.name)) {
                                allFestivals.add(
                                    FestivalItem(festival.name, festival.emoji, "api")
                                )
                            }
                        }
                    }
                    
                    // 2. 添加订阅的节日（但排除已经在API节日列表中的，避免重复）
                    subscribedEvents.forEach { event ->
                        // 提取emoji和名称（支持中文）
                        val (emoji, name) = extractEmojiAndName(event.title)
                        
                        // 检查是否已经在API节日列表中（避免重复）
                        val isInApiFestivals = response.festivals?.any { festival ->
                            val festivalNamePart = festival.name.split("/").firstOrNull()?.trim() ?: festival.name
                            val eventNamePart = name.split("/")[0].trim()
                            // 精确匹配或部分匹配
                            festival.name.equals(name, ignoreCase = true) ||
                            festival.name.contains(name, ignoreCase = true) ||
                            name.contains(festivalNamePart, ignoreCase = true) ||
                            festivalNamePart.equals(eventNamePart, ignoreCase = true)
                        } ?: false
                        
                        // 如果不在API节日列表中，且用户订阅了，则添加订阅的节日
                        // 这样可以显示那些API没有返回但用户订阅了的节日
                        if (!isInApiFestivals && festivalSubscriptionManager.isSubscribed(name)) {
                            allFestivals.add(
                                FestivalItem(name, emoji, "subscribed")
                            )
                        }
                    }
                    
                    // 注意：现在只显示已订阅的节日（方案A：API节日作为默认订阅，支持个性化控制）
                    
                    // 为每个节日创建独立的小卡片（使用不同颜色区分）
                    if (allFestivals.isNotEmpty()) {
                        allFestivals.forEachIndexed { index, festival ->
                            // 使用渐变色：从粉红到紫色到蓝色
                            val cardColor = when (index % 4) {
                                0 -> "#F8BBD0" // 粉红色系
                                1 -> "#E1BEE7" // 紫色系
                                2 -> "#BBDEFB" // 蓝色系
                                else -> "#C5E1A5" // 绿色系
                            }
                            
                            addFestivalCard(
                                "${festival.emoji} ${festival.name}",
                                "点击查看详情",
                                cardColor,
                                true, // 节日可点击
                                festival.name,
                                festival.emoji,
                                dateStr
                            )
                        }
                        tvHolidayHint.visibility = View.VISIBLE
                    } else {
                        // 没有节日，显示提示卡片（不重复显示农历）
                        if (!response.isHoliday) {
                            addFestivalCard(
                                "📅 今日无特殊节日",
                                "享受平凡的一天 ☀️",
                                "#ECEFF1", // 灰蓝色系
                                false,
                                "", "", ""
                            )
                        }
                        tvHolidayHint.visibility = View.GONE
                    }
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    festivalCardsContainer.removeAllViews()
                    addFestivalCard(
                        "❌ 加载失败",
                        "请检查网络连接或稍后重试",
                        "#FFCDD2", // 红色系 - 错误提示
                        false,
                        "", "", ""
                    )
                }
            }
        }
    }
    
    /**
     * 动态创建节日卡片
     */
    private fun addFestivalCard(
        title: String,
        subtitle: String,
        backgroundColor: String,
        clickable: Boolean,
        festivalName: String,
        festivalEmoji: String,
        dateStr: String
    ) {
        // 创建卡片布局
        val cardView = MaterialCardView(context).apply {
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply {
                bottomMargin = (8 * resources.displayMetrics.density).toInt() // 8dp间距
            }
            setCardBackgroundColor(android.graphics.Color.parseColor(backgroundColor))
            radius = (12 * resources.displayMetrics.density)
            cardElevation = (2 * resources.displayMetrics.density)
            setContentPadding(
                (16 * resources.displayMetrics.density).toInt(),
                (12 * resources.displayMetrics.density).toInt(),
                (16 * resources.displayMetrics.density).toInt(),
                (12 * resources.displayMetrics.density).toInt()
            )
        }
        
        // 创建内容布局（垂直）
        val contentLayout = LinearLayout(context).apply {
            orientation = LinearLayout.VERTICAL
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            )
        }
        
        // 标题
        val titleView = TextView(context).apply {
            text = title
            textSize = 18f
            setTypeface(null, android.graphics.Typeface.BOLD)
            setTextColor(android.graphics.Color.parseColor("#4A148C"))
        }
        
        // 副标题
        val subtitleView = TextView(context).apply {
            text = subtitle
            textSize = 14f
            setTextColor(android.graphics.Color.parseColor("#6A1B9A"))
            setPadding(0, (4 * resources.displayMetrics.density).toInt(), 0, 0)
        }
        
        contentLayout.addView(titleView)
        contentLayout.addView(subtitleView)
        cardView.addView(contentLayout)
        
        // 设置点击事件（如果可点击）
        if (clickable && festivalName.isNotEmpty()) {
            cardView.setOnClickListener {
                val intent = Intent(context, FestivalDetailActivity::class.java).apply {
                    putExtra("festival_name", festivalName)
                    putExtra("festival_emoji", festivalEmoji)
                    putExtra("date", dateStr)
                }
                context.startActivity(intent)
            }
            
            // 添加点击效果
            cardView.isClickable = true
            cardView.isFocusable = true
            val outValue = android.util.TypedValue()
            context.theme.resolveAttribute(
                android.R.attr.selectableItemBackground,
                outValue,
                true
            )
            cardView.foreground = context.getDrawable(outValue.resourceId)
        }
        
        festivalCardsContainer.addView(cardView)
    }
    
    /**
     * 从事件标题中提取emoji和名称（支持中文）
     */
    private fun extractEmojiAndName(title: String): Pair<String, String> {
        // 尝试提取emoji（通常是开头的特殊字符）
        val emojiRegex = Regex("""[\p{So}\p{Cn}\p{Emoji}]+""")
        val emojiMatch = emojiRegex.find(title)
        val emoji = emojiMatch?.value?.trim() ?: "🎊"
        
        // 提取名称（去掉emoji后的部分）
        val name = if (emojiMatch != null) {
            title.removeRange(emojiMatch.range).trim()
        } else {
            title.trim()
        }
        
        return Pair(emoji, name.ifEmpty { title })
    }
    
    /**
     * 从事件标题中提取节日名称（用于去重）
     */
    private fun extractFestivalNameFromTitle(title: String): String {
        val (_, name) = extractEmojiAndName(title)
        return name
    }
    
}


package com.ncu.kotlincalendar.ui.managers

import android.content.Context
import android.widget.TextView
import java.text.SimpleDateFormat
import java.util.*
import kotlin.math.abs

/**
 * 今日运势管理器（智能版）
 * 
 * 职责：
 * - 结合天气和节气生成智能运势
 * - 基于真实天气条件调整宜忌建议
 * - 计算今日幸运指数（考虑天气因素）
 * 
 * 算法说明：
 * 1. 检查是否是二十四节气，节气优先影响宜忌
 * 2. 获取实时天气，根据天气调整活动建议
 * 3. 根据温度调整运势分数
 * 4. 生成实用的温馨提示
 * 
 * 使用方式：
 * ```kotlin
 * val fortuneManager = FortuneManager(context, tvFortuneContent, weatherManager)
 * fortuneManager.loadFortune()
 * ```
 */
class FortuneManager(
    private val context: Context,
    private val tvFortuneContent: TextView,
    private val weatherManager: WeatherManager? = null  // 可选的天气管理器
) {
    
    private val dayOfWeek = listOf("日", "一", "二", "三", "四", "五", "六")
    
    // 二十四节气数据（2025年）
    data class SolarTerm(
        val name: String,
        val desc: String,
        val boost: List<String>,  // 推荐的宜事
        val reduce: List<String>  // 不推荐的忌事
    )
    
    private val solarTerms = mapOf(
        "01-05" to SolarTerm("小寒", "天气寒冷，宜养生保暖", listOf("读书", "沐浴", "求医"), listOf("出行", "动土")),
        "01-20" to SolarTerm("大寒", "一年中最冷的时节", listOf("祭祀", "祈福", "修造"), listOf("移徙", "嫁娶")),
        "02-03" to SolarTerm("立春", "春季开始，万物复苏", listOf("开市", "求财", "纳财", "会友"), listOf("安葬", "破土")),
        "02-18" to SolarTerm("雨水", "降雨增多，气温回升", listOf("栽种", "祈福", "开市"), listOf("动土", "修造")),
        "03-05" to SolarTerm("惊蛰", "春雷惊醒蛰伏", listOf("出行", "交易", "求财", "会友"), listOf("安床", "移徙")),
        "03-20" to SolarTerm("春分", "昼夜平分，春意盎然", listOf("嫁娶", "纳采", "祭祀"), listOf("诉讼", "词讼")),
        "04-04" to SolarTerm("清明", "天清地明，祭祖扫墓", listOf("祭祀", "扫舍"), listOf("嫁娶", "开市")),
        "04-20" to SolarTerm("谷雨", "雨生百谷，播种佳时", listOf("栽种", "开市", "纳财"), listOf("移徙", "入宅")),
        "05-05" to SolarTerm("立夏", "夏季开始，气温升高", listOf("出行", "会友", "交易"), listOf("动土", "破土")),
        "05-21" to SolarTerm("小满", "麦类作物籽粒饱满", listOf("纳财", "开市", "求财"), listOf("诉讼", "安葬")),
        "06-05" to SolarTerm("芒种", "有芒作物成熟", listOf("栽种", "纳财", "开市"), listOf("嫁娶", "移徙")),
        "06-21" to SolarTerm("夏至", "白昼最长，阳气最盛", listOf("祈福", "求财", "交易"), listOf("词讼", "安葬")),
        "07-07" to SolarTerm("小暑", "天气炎热，注意防暑", listOf("沐浴", "求医", "治病"), listOf("嫁娶", "移徙", "出行")),
        "07-22" to SolarTerm("大暑", "一年中最热的时节", listOf("沐浴", "扫舍", "解除"), listOf("出行", "开市", "动土")),
        "08-07" to SolarTerm("立秋", "秋季开始，暑去凉来", listOf("开市", "求财", "交易"), listOf("嫁娶", "移徙")),
        "08-23" to SolarTerm("处暑", "炎热结束，秋高气爽", listOf("出行", "会友", "祭祀"), listOf("安葬", "破土")),
        "09-07" to SolarTerm("白露", "天气转凉，露水增多", listOf("求医", "治病", "沐浴"), listOf("嫁娶", "移徙")),
        "09-23" to SolarTerm("秋分", "昼夜平分，丰收时节", listOf("纳财", "开市", "祭祀"), listOf("诉讼", "词讼")),
        "10-08" to SolarTerm("寒露", "露水将凝，气温下降", listOf("祈福", "祭祀", "求医"), listOf("嫁娶", "开市")),
        "10-23" to SolarTerm("霜降", "天气渐冷，初霜出现", listOf("纳财", "开市", "修造"), listOf("移徙", "出行")),
        "11-07" to SolarTerm("立冬", "冬季开始，万物收藏", listOf("祭祀", "修造", "纳财"), listOf("嫁娶", "移徙", "出行")),
        "11-22" to SolarTerm("小雪", "开始降雪，气温降低", listOf("祭祀", "祈福", "修造"), listOf("嫁娶", "出行")),
        "12-07" to SolarTerm("大雪", "降雪增多，严寒将至", listOf("修造", "祭祀", "沐浴"), listOf("嫁娶", "移徙", "出行")),
        "12-21" to SolarTerm("冬至", "阴极阳生，白昼最短", listOf("祭祀", "祈福", "沐浴"), listOf("嫁娶", "移徙"))
    )
    
    // 黄历宜事列表
    private val goodThings = listOf(
        "出行", "会友", "开市", "祈福", "求财", "纳财", "交易",
        "立券", "移徙", "嫁娶", "祭祀", "安床", "入宅", "动土",
        "修造", "纳采", "订盟", "安葬", "破土", "启攒", "除服",
        "成服", "塞穴", "筑堤", "理发", "整手足甲", "求医", "治病",
        "针灸", "沐浴", "扫舍", "修饰垣墙", "平治道涂", "破屋",
        "坏垣", "裁衣", "作灶", "解除", "开渠", "掘井", "安门",
        "竖柱", "上梁", "盖屋", "作梁", "修仓", "经络", "酝酿",
        "开池", "栽种", "牧养", "纳畜", "捕捉", "畋猎", "结网",
        "取渔", "伐木", "架马", "断蚁", "归岫"
    )
    
    // 黄历忌事列表
    private val badThings = listOf(
        "诉讼", "词讼", "动土", "破土", "安葬", "开市", "交易",
        "纳财", "出货财", "栽种", "嫁娶", "移徙", "入宅", "安床",
        "作灶", "修造", "动土", "竖柱", "上梁", "盖屋", "探病",
        "针灸", "出行", "祈福", "祭祀", "纳采", "订盟", "会亲友",
        "进人口", "裁衣", "冠笄", "解除", "求医", "治病", "造畜稠",
        "修饰垣墙", "平治道涂", "破屋", "坏垣", "伐木", "架马",
        "斋醮", "开渠", "掘井", "筑堤", "开池", "造船", "捕捉",
        "畋猎", "结网", "取渔", "纳畜", "牧养", "断蚁"
    )
    
    // 幸运色列表
    private val luckyColors = listOf(
        "红色", "橙色", "黄色", "绿色", "青色", "蓝色", 
        "紫色", "粉色", "白色", "金色", "银色", "米色"
    )
    
    // 五行元素
    private val elements = listOf("金", "木", "水", "火", "土")
    
    // 星座运势描述
    private val fortuneDescriptions = listOf(
        "今日运势极佳，万事顺意！",
        "运势平稳，适宜稳扎稳打。",
        "小有波折，需谨慎行事。",
        "运势上扬，把握机会！",
        "诸事顺利，心情愉悦。",
        "运势一般，保持平常心。",
        "运势渐好，积极进取！"
    )
    
    /**
     * 加载今日运势（智能版：结合天气和节气）
     */
    fun loadFortune(currentWeather: String? = null, currentTemp: String? = null) {
        val calendar = Calendar.getInstance()
        val date = calendar.time
        val dateFormat = SimpleDateFormat("yyyy年MM月dd日", Locale.CHINA)
        val monthDayFormat = SimpleDateFormat("MM-dd", Locale.CHINA)
        val dateStr = dateFormat.format(date)
        val monthDay = monthDayFormat.format(date)
        val weekDay = dayOfWeek[calendar.get(Calendar.DAY_OF_WEEK) - 1]
        val currentDayOfWeek = calendar.get(Calendar.DAY_OF_WEEK)
        
        // 检查是否是节气
        val solarTerm = solarTerms[monthDay]
        val dateDisplay = if (solarTerm != null) {
            "$dateStr 星期$weekDay • ${solarTerm.name}"
        } else {
            "$dateStr 星期$weekDay"
        }
        
        // 基于日期计算种子值（确保同一天运势相同）
        val seed = calendar.get(Calendar.YEAR) * 10000 +
                   calendar.get(Calendar.MONTH) * 100 +
                   calendar.get(Calendar.DAY_OF_MONTH)
        val random = Random(seed.toLong())
        
        // 基础宜忌列表（可变）
        var baseGoodThings = goodThings.toMutableList()
        var baseBadThings = badThings.toMutableList()
        
        // 如果是节气，调整宜忌（节气优先）
        solarTerm?.let { term ->
            // 将节气推荐的事项提升到前面
            term.boost.forEach { item ->
                baseGoodThings.remove(item)
                baseGoodThings.add(0, item)
            }
            // 将节气不推荐的事项提升到忌事前面
            term.reduce.forEach { item ->
                baseBadThings.remove(item)
                baseBadThings.add(0, item)
            }
        }
        
        // 根据天气调整宜忌
        currentWeather?.let { weather ->
            when {
                weather.contains("晴") -> {
                    // 晴天适合外出活动
                    listOf("出行", "会友", "祈福", "求财").forEach { item ->
                        baseGoodThings.remove(item)
                        baseGoodThings.add(0, item)
                    }
                }
                weather.contains("雨") -> {
                    // 雨天适合室内活动
                    listOf("读书", "沐浴", "扫舍", "修造").forEach { item ->
                        baseGoodThings.remove(item)
                        baseGoodThings.add(0, item)
                    }
                    listOf("出行", "移徙", "嫁娶").forEach { item ->
                        baseBadThings.remove(item)
                        baseBadThings.add(0, item)
                    }
                }
                weather.contains("雪") -> {
                    listOf("祭祀", "祈福", "沐浴").forEach { item ->
                        baseGoodThings.remove(item)
                        baseGoodThings.add(0, item)
                    }
                    listOf("出行", "嫁娶", "移徙", "开市").forEach { item ->
                        baseBadThings.remove(item)
                        baseBadThings.add(0, item)
                    }
                }
                weather.contains("阴") || weather.contains("云") -> {
                    listOf("祭祀", "修造", "求医").forEach { item ->
                        baseGoodThings.remove(item)
                        baseGoodThings.add(0, item)
                    }
                }
            }
        }
        
        // 选择宜忌
        val goodCount = 4 + random.nextInt(4) // 4-7项
        val badCount = 3 + random.nextInt(3)  // 3-5项
        
        val todayGood = mutableSetOf<String>()
        val todayBad = mutableSetOf<String>()
        
        // 优先从调整后的列表前面选择
        for (i in 0 until minOf(goodCount, baseGoodThings.size)) {
            todayGood.add(baseGoodThings[i])
        }
        
        while (todayGood.size < goodCount) {
            todayGood.add(baseGoodThings[random.nextInt(baseGoodThings.size)])
        }
        
        for (i in 0 until minOf(badCount, baseBadThings.size)) {
            if (baseBadThings[i] !in todayGood) {
                todayBad.add(baseBadThings[i])
            }
        }
        
        while (todayBad.size < badCount) {
            val bad = baseBadThings[random.nextInt(baseBadThings.size)]
            if (bad !in todayGood) {
                todayBad.add(bad)
            }
        }
        
        // 计算幸运元素
        val luckyColor = luckyColors[random.nextInt(luckyColors.size)]
        val luckyNumber = random.nextInt(100)
        val luckyElement = elements[random.nextInt(elements.size)]
        
        // 基础运势分数
        var baseScore = 60 + random.nextInt(40)
        
        // 根据天气调整分数
        currentWeather?.let { weather ->
            when {
                weather.contains("晴") -> baseScore += 5
                weather.contains("雨") || weather.contains("雪") -> baseScore -= 3
            }
        }
        
        currentTemp?.let { temp ->
            val temperature = temp.toIntOrNull() ?: 20
            when {
                temperature in 15..25 -> baseScore += 3  // 舒适温度
                temperature > 35 || temperature < 0 -> baseScore -= 5  // 极端温度
            }
        }
        
        // 确保分数在60-99范围内
        val fortuneScore = maxOf(60, minOf(99, baseScore))
        
        // 生成运势描述
        val fortuneDesc = when {
            solarTerm != null -> "今日${solarTerm.name}，${solarTerm.desc}。"
            currentWeather?.contains("晴") == true -> "天气晴朗，运势上扬，把握机会！"
            currentWeather?.contains("雨") == true -> "雨天宜静养，适合思考和规划。"
            currentWeather?.contains("雪") == true -> "雪天出行需谨慎，适合室内活动。"
            else -> fortuneDescriptions[random.nextInt(fortuneDescriptions.size)]
        }
        
        // 构建运势内容
        val fortuneText = buildString {
            append("📅 $dateDisplay\n\n")
            
            append("【运势指数】\n")
            append("综合运势：${getStarRating(fortuneScore)} (${fortuneScore}分)\n")
            append("$fortuneDesc\n\n")
            
            append("【黄历宜忌】\n")
            append("✅ 宜：${todayGood.joinToString("、")}\n\n")
            append("❌ 忌：${todayBad.joinToString("、")}\n\n")
            
            append("【幸运元素】\n")
            append("🎨 幸运色：$luckyColor\n")
            append("🔢 幸运数字：$luckyNumber\n")
            append("⚡ 五行：$luckyElement\n\n")
            
            append("【温馨提示】\n")
            append(getSmartTip(currentDayOfWeek, currentWeather, currentTemp, solarTerm))
        }
        
        tvFortuneContent.text = fortuneText
    }
    
    /**
     * 将分数转换为星级评分
     */
    private fun getStarRating(score: Int): String {
        val stars = when {
            score >= 90 -> "⭐⭐⭐⭐⭐"
            score >= 80 -> "⭐⭐⭐⭐"
            score >= 70 -> "⭐⭐⭐"
            score >= 60 -> "⭐⭐"
            else -> "⭐"
        }
        return stars
    }
    
    /**
     * 智能温馨提示（结合天气、节气、星期）
     */
    private fun getSmartTip(dayOfWeek: Int, weather: String?, temp: String?, solarTerm: SolarTerm?): String {
        var tip = ""
        
        // 基于天气的提示
        weather?.let { w ->
            tip = when {
                w.contains("雨") -> "今日有雨，出门记得带伞哦！☔ "
                w.contains("雪") -> "今日下雪，注意保暖防滑！❄️ "
                w.contains("晴") -> "今日晴朗，适合户外活动！☀️ "
                w.contains("雾") || w.contains("霾") -> "今日有雾霾，减少外出，注意健康！😷 "
                else -> ""
            }
        }
        
        // 基于温度的提示
        temp?.let { t ->
            val temperature = t.toIntOrNull() ?: 20
            tip += when {
                temperature > 30 -> "高温天气，多补充水分！🥤"
                temperature < 5 -> "寒冷天气，注意保暖！🧣"
                temperature in 15..25 -> "温度适宜，心情愉悦！😊"
                else -> ""
            }
        }
        
        // 如果没有天气数据，使用星期提示
        if (tip.isEmpty()) {
            tip = when (dayOfWeek) {
                Calendar.SUNDAY -> "周日放松，为新的一周充电！⚡"
                Calendar.MONDAY -> "周一元气满满！新的一周，加油开始！💪"
                Calendar.TUESDAY -> "保持节奏，稳步前进！🚀"
                Calendar.WEDNESDAY -> "周三已过半，坚持就是胜利！🌟"
                Calendar.THURSDAY -> "临近周末，再努力一把！💫"
                Calendar.FRIDAY -> "愉快的周五，周末即将到来！🎉"
                Calendar.SATURDAY -> "周末愉快，享受休闲时光！🌈"
                else -> "祝你今天开心顺利！😊"
            }
        }
        
        // 如果是节气，添加节气提示
        solarTerm?.let { term ->
            tip = "${term.name}：${term.desc}。$tip"
        }
        
        return tip
    }
    
    companion object {
        private const val TAG = "FortuneManager"
    }
}


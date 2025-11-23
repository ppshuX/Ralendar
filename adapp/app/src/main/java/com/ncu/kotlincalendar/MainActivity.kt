package com.ncu.kotlincalendar

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.Button
import android.widget.ImageButton
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import com.google.android.material.textfield.TextInputEditText
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.kizitonwose.calendar.core.CalendarDay
import com.kizitonwose.calendar.core.CalendarMonth
import com.kizitonwose.calendar.core.DayPosition
import com.kizitonwose.calendar.core.daysOfWeek
import com.kizitonwose.calendar.view.CalendarView
import com.kizitonwose.calendar.view.MonthDayBinder
import com.kizitonwose.calendar.view.MonthScrollListener
import com.kizitonwose.calendar.view.ViewContainer
import com.kizitonwose.calendar.view.WeekCalendarView
import com.kizitonwose.calendar.view.WeekDayBinder
import com.ncu.kotlincalendar.api.client.RetrofitClient
import com.ncu.kotlincalendar.data.database.AppDatabase
import com.ncu.kotlincalendar.data.database.EventDao
import com.ncu.kotlincalendar.data.database.SubscriptionDao
import com.ncu.kotlincalendar.data.models.Event
import com.ncu.kotlincalendar.data.models.Subscription
import com.ncu.kotlincalendar.data.managers.ReminderManager
import com.ncu.kotlincalendar.data.managers.SubscriptionManager
import com.ncu.kotlincalendar.data.repository.EventRepository
import com.ncu.kotlincalendar.ui.managers.WeatherManager
import com.ncu.kotlincalendar.ui.managers.HolidayManager
import com.ncu.kotlincalendar.ui.managers.FortuneManager
import com.ncu.kotlincalendar.ui.dialogs.EventEditDialogHelper
import com.ncu.kotlincalendar.utils.PreferenceManager
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import kotlinx.coroutines.Job
import kotlinx.coroutines.cancel
import java.text.SimpleDateFormat
import java.time.Instant
import java.time.LocalDate
import java.time.YearMonth
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.*

class MainActivity : AppCompatActivity() {
    
    private lateinit var calendarView: CalendarView
    private lateinit var weekCalendarView: WeekCalendarView
    private lateinit var weekTimelineRecycler: RecyclerView
    private lateinit var weekTimelineAdapter: TimeSlotAdapter
    private lateinit var dayViewRecycler: RecyclerView
    private lateinit var dayViewAdapter: TimeSlotAdapter
    private lateinit var monthViewCard: com.google.android.material.card.MaterialCardView
    private lateinit var weekViewContainer: android.widget.LinearLayout
    private lateinit var dayViewCard: com.google.android.material.card.MaterialCardView
    private lateinit var bottomContentCard: com.google.android.material.card.MaterialCardView
    private lateinit var tvSelectedDate: TextView
    private lateinit var tvMonthYear: TextView
    private lateinit var btnPreviousMonth: ImageButton
    private lateinit var btnNextMonth: ImageButton
    private lateinit var btnViewSwitch: Button
    private lateinit var btnAddEvent: Button
    private lateinit var btnAICreate: Button
    private lateinit var btnSubscribe: Button
    private lateinit var btnCloudMode: Button
    private lateinit var recyclerView: RecyclerView
    private lateinit var adapter: EventAdapter
    
    // Tab 和内容视图
    private lateinit var tabLayout: com.google.android.material.tabs.TabLayout
    private lateinit var weatherCard: com.google.android.material.card.MaterialCardView
    private lateinit var tvWeatherLocation: TextView
    private lateinit var tvTemperature: TextView
    private lateinit var tvWeatherDesc: TextView
    private lateinit var tvFeelsLike: TextView
    private lateinit var tvHumidity: TextView
    private lateinit var tvWind: TextView
    private lateinit var scrollViewHoliday: android.widget.LinearLayout
    private lateinit var scrollViewFortune: android.widget.LinearLayout
    private lateinit var festivalCardsContainer: LinearLayout
    private lateinit var tvHolidayHint: TextView
    private lateinit var tvFortuneContent: TextView
    
    private lateinit var database: AppDatabase
    private lateinit var eventDao: EventDao
    private lateinit var subscriptionDao: SubscriptionDao
    private lateinit var eventRepository: EventRepository
    private lateinit var reminderManager: ReminderManager
    private lateinit var subscriptionManager: SubscriptionManager
    private val eventsList = mutableListOf<Event>()
    private lateinit var weatherManager: WeatherManager
    private lateinit var holidayManager: HolidayManager
    private lateinit var fortuneManager: FortuneManager
    private var selectedDate: LocalDate? = LocalDate.now()
    private var currentMonth: YearMonth = YearMonth.now()
    private val datesWithEvents = mutableSetOf<LocalDate>()
    private val datesWithFestivals = mutableMapOf<LocalDate, String>()
    private var currentTab: Int = 0
    private var viewMode: Int = 0
    private var loadEventsJob: Job? = null
    private var tabListener: com.google.android.material.tabs.TabLayout.OnTabSelectedListener? = null
    private lateinit var eventEditDialogHelper: EventEditDialogHelper
    
    inner class DayViewContainer(view: View) : ViewContainer(view) {
        val textView: TextView = view.findViewById(R.id.calendarDayText)
        val dotView: View = view.findViewById(R.id.calendarDayDot)
        val festivalLabel: TextView = view.findViewById(R.id.calendarDayFestivalLabel)
        
        lateinit var day: CalendarDay
        
        init {
            view.setOnClickListener {
                if (day.position == DayPosition.MonthDate) {
                    selectDate(day.date)
                }
            }
        }
    }
    
    inner class WeekDayViewContainer(view: View) : ViewContainer(view) {
        val dayText: TextView = view.findViewById(R.id.weekDayText)
        val numberText: TextView = view.findViewById(R.id.weekDayNumber)
        val dotView: View = view.findViewById(R.id.weekDayDot)
        val festivalLabel: TextView = view.findViewById(R.id.weekDayFestivalLabel)
        
        lateinit var day: com.kizitonwose.calendar.core.WeekDay
        
        init {
            view.setOnClickListener {
                selectDate(day.date)
            }
        }
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        database = AppDatabase.getDatabase(this)
        eventDao = database.eventDao()
        subscriptionDao = database.subscriptionDao()
        eventRepository = EventRepository(this)
        reminderManager = ReminderManager(this)
        subscriptionManager = SubscriptionManager(
            subscriptionDao,
            eventDao,
            RetrofitClient.api
        )
        calendarView = findViewById(R.id.calendarView)
        weekCalendarView = findViewById(R.id.weekCalendarView)
        weekTimelineRecycler = findViewById(R.id.weekTimelineRecycler)
        dayViewRecycler = findViewById(R.id.dayViewRecycler)
        monthViewCard = findViewById(R.id.monthViewCard)
        weekViewContainer = findViewById(R.id.weekViewContainer)
        dayViewCard = findViewById(R.id.dayViewCard)
        bottomContentCard = findViewById(R.id.bottomContentCard)
        tvSelectedDate = findViewById(R.id.tvSelectedDate)
        tvMonthYear = findViewById(R.id.tvMonthYear)
        btnPreviousMonth = findViewById(R.id.btnPreviousMonth)
        btnNextMonth = findViewById(R.id.btnNextMonth)
        btnViewSwitch = findViewById(R.id.btnViewSwitch)
        btnAddEvent = findViewById(R.id.btnAddEvent)
        btnAICreate = findViewById(R.id.btnAICreate)
        btnSubscribe = findViewById(R.id.btnSubscribe)
        btnCloudMode = findViewById(R.id.btnCloudMode)
        recyclerView = findViewById(R.id.recyclerView)
        tabLayout = findViewById(R.id.tabLayout)
        weatherCard = findViewById(R.id.weatherCard)
        tvWeatherLocation = findViewById(R.id.tvWeatherLocation)
        tvTemperature = findViewById(R.id.tvTemperature)
        tvWeatherDesc = findViewById(R.id.tvWeatherDesc)
        tvFeelsLike = findViewById(R.id.tvFeelsLike)
        tvHumidity = findViewById(R.id.tvHumidity)
        tvWind = findViewById(R.id.tvWind)
        scrollViewHoliday = findViewById(R.id.scrollViewHoliday)
        scrollViewFortune = findViewById(R.id.scrollViewFortune)
        festivalCardsContainer = findViewById(R.id.festivalCardsContainer)
        tvHolidayHint = findViewById(R.id.tvHolidayHint)
        tvFortuneContent = findViewById(R.id.tvFortuneContent)
        
        weatherManager = WeatherManager(
            this, weatherCard, tvWeatherLocation, tvTemperature,
            tvWeatherDesc, tvFeelsLike, tvHumidity, tvWind
        )
        holidayManager = HolidayManager(
            festivalCardsContainer, tvHolidayHint, this, subscriptionManager
        )
        fortuneManager = FortuneManager(this, tvFortuneContent)
        adapter = EventAdapter(
            events = emptyList(),
            onItemClick = { event -> showEventDetails(event) },
            onItemLongClick = { event -> showDeleteConfirmDialog(event) }
        )
        recyclerView.layoutManager = LinearLayoutManager(this)
        recyclerView.adapter = adapter
        weekTimelineAdapter = TimeSlotAdapter(
            events = emptyList(),
            onEventClick = { event ->
                showEventDetails(event)
            }
        )
        weekTimelineRecycler.layoutManager = LinearLayoutManager(this)
        weekTimelineRecycler.adapter = weekTimelineAdapter
        dayViewAdapter = TimeSlotAdapter(
            events = emptyList(),
            onEventClick = { event -> showEventDetails(event) }
        )
        dayViewRecycler.layoutManager = LinearLayoutManager(this)
        dayViewRecycler.adapter = dayViewAdapter
        tabLayout.addTab(tabLayout.newTab().setText("📅 日程安排"))
        tabLayout.addTab(tabLayout.newTab().setText("🎊 今日节日"))
        tabLayout.addTab(tabLayout.newTab().setText("🔮 今日运势"))
        tabListener = object : com.google.android.material.tabs.TabLayout.OnTabSelectedListener {
            override fun onTabSelected(tab: com.google.android.material.tabs.TabLayout.Tab?) {
                currentTab = tab?.position ?: 0
                selectedDate?.let { date ->
                    val millis = date.atStartOfDay(ZoneId.systemDefault()).toInstant().toEpochMilli()
                    when (currentTab) {
                        0 -> {
                            switchContent(0)
                            loadEventsJob?.cancel()
                            updateEventsList()
                            loadEventsJob = lifecycleScope.launch(Dispatchers.IO) {
                                try {
                                    if (eventsList.isEmpty()) {
                                        loadAllEventsSync()
                                    } else {
                                        loadEventsForSelectedDate(millis)
                                    }
                                } catch (e: Exception) {
                                    withContext(Dispatchers.Main) {
                                        updateEventsList()
                                    }
                                }
                            }
                        }
                        1 -> {
                            switchContent(1)
                            loadHolidayInfo(millis)
                        }
                        2 -> {
                            switchContent(2)
                            fortuneManager.loadFortune(
                                weatherManager.currentWeather,
                                weatherManager.currentTemperature
                            )
                        }
                    }
                }
            }
            
            override fun onTabUnselected(tab: com.google.android.material.tabs.TabLayout.Tab?) {}
            override fun onTabReselected(tab: com.google.android.material.tabs.TabLayout.Tab?) {}
        }
        tabLayout.addOnTabSelectedListener(tabListener)
        
        eventEditDialogHelper = EventEditDialogHelper(this, object : EventEditDialogHelper.OnEventSaveCallback {
            override fun onSave(
                event: Event?,
                title: String,
                description: String,
                dateTime: Long,
                reminderMinutes: Int,
                locationName: String,
                latitude: Double,
                longitude: Double
            ) {
                if (event != null) {
                    updateEvent(
                        event.id,
                        title,
                        description,
                        dateTime,
                        reminderMinutes,
                        locationName,
                        latitude,
                        longitude
                    )
                } else {
                    addEvent(
                        title,
                        description,
                        dateTime,
                        reminderMinutes,
                        locationName,
                        latitude,
                        longitude
                    )
                }
            }
        })
        
        setupCalendar()
        setupWeekCalendar()
        updateDateDisplay(selectedDate!!)
        updateEventsList()
        loadAllEvents()
        com.ncu.kotlincalendar.data.managers.FestivalSubscriptionManager(this).initDefaultFestivals()
        selectedDate?.let { date ->
            val millis = date.atStartOfDay(ZoneId.systemDefault()).toInstant().toEpochMilli()
            loadHolidayInfo(millis)
        }
        updateCalendarDots()
        btnPreviousMonth.setOnClickListener {
            currentMonth = currentMonth.minusMonths(1)
            calendarView.scrollToMonth(currentMonth)
        }
        
        btnNextMonth.setOnClickListener {
            currentMonth = currentMonth.plusMonths(1)
            calendarView.scrollToMonth(currentMonth)
        }
        
        // 三视图切换按钮
        btnViewSwitch.setOnClickListener {
            viewMode = (viewMode + 1) % 3
            switchViewMode(viewMode)
        }
        
        switchViewMode(0)
        
        btnAddEvent.setOnClickListener {
            showAddEventDialog()
        }
        
        btnAICreate.setOnClickListener {
            showAIEventDialog()
        }
        
        btnSubscribe.setOnClickListener {
            val intent = android.content.Intent(this, SubscriptionsActivity::class.java)
            startActivity(intent)
        }
        
        btnCloudMode.setOnClickListener {
            toggleCloudMode()
        }
        
        updateCloudModeButton()
        
        Toast.makeText(this, "📅 日历已加载，数据会自动保存", Toast.LENGTH_SHORT).show()
        
        lifecycleScope.launch {
            delay(200)
            weatherManager.loadWeather(lifecycleScope)
        }
        
        // 请求通知权限（Android 13+）
        requestNotificationPermission()
        
        // 处理从通知跳转过来的情况
        handleNotificationIntent()
    }
    
    /**
     * 处理从通知跳转过来的情况
     * 如果是点击通知跳转过来的，自动选中对应的事件并显示详情
     */
    private fun handleNotificationIntent() {
        val fromNotification = intent.getBooleanExtra("fromNotification", false)
        if (fromNotification) {
            val eventId = intent.getLongExtra("eventId", -1)
            if (eventId > 0) {
                lifecycleScope.launch {
                    delay(500)
                    withContext(Dispatchers.IO) {
                        try {
                            val event: Event? = if (PreferenceManager.isCloudMode(this@MainActivity) && PreferenceManager.isLoggedIn(this@MainActivity)) {
                                val result = eventRepository.getAllEvents()
                                result.getOrNull()?.find { it.id == eventId }
                            } else {
                                eventDao.getAllEvents().find { it.id == eventId }
                            }
                            
                            event?.let {
                                withContext(Dispatchers.Main) {
                                    val eventDate = Instant.ofEpochMilli(it.dateTime)
                                        .atZone(ZoneId.systemDefault())
                                        .toLocalDate()
                                    
                                    selectedDate = eventDate
                                    updateDateDisplay(eventDate)
                                    calendarView.notifyCalendarChanged()
                                    weekCalendarView.scrollToWeek(eventDate)
                                    
                                    loadAllEvents()
                                    val eventDateMillis = eventDate.atStartOfDay(ZoneId.systemDefault()).toInstant().toEpochMilli()
                                    loadEventsForSelectedDate(eventDateMillis)
                                    
                                    delay(300)
                                    showEventDetails(it)
                                }
                            }
                        } catch (e: Exception) {
                        }
                    }
                }
            }
        }
    }
    
    /**
     * 当Activity恢复时刷新数据（从订阅页面返回时）
     */
    override fun onResume() {
        super.onResume()
        updateCalendarDots()
        selectedDate?.let { date ->
            val millis = date.atStartOfDay(ZoneId.systemDefault()).toInstant().toEpochMilli()
            loadHolidayInfo(millis)
            if (eventsList.isEmpty()) {
                loadAllEvents()
                loadEventsForSelectedDate(millis)
            } else {
                updateEventsList()
            }
        }
        weatherManager.loadWeather(lifecycleScope)
    }
    
    override fun onDestroy() {
        super.onDestroy()
        
        loadEventsJob?.cancel()
        loadEventsJob = null
        tabListener?.let { listener ->
            try {
                tabLayout.removeOnTabSelectedListener(listener)
            } catch (e: Exception) {
                Log.w("MainActivity", "清理Tab监听器失败", e)
            }
        }
        tabListener = null
        
        eventsList.clear()
        datesWithEvents.clear()
        datesWithFestivals.clear()
    }
    
    // 请求通知权限
    private fun requestNotificationPermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(
                    this,
                    Manifest.permission.POST_NOTIFICATIONS
                ) != PackageManager.PERMISSION_GRANTED
            ) {
                ActivityCompat.requestPermissions(
                    this,
                    arrayOf(Manifest.permission.POST_NOTIFICATIONS),
                    1001
                )
            }
        }
    }
    
    private fun showDate(timeInMillis: Long) {
        val dateFormat = SimpleDateFormat("yyyy年MM月dd日 EEEE", Locale.CHINESE)
        val dateStr = dateFormat.format(Date(timeInMillis))
        tvSelectedDate.text = "选中日期：$dateStr"
    }
    
    // 处理Activity返回结果
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        
        if (requestCode == MapPickerActivity.REQUEST_CODE_MAP_PICKER && resultCode == RESULT_OK && data != null) {
            val locationName = data.getStringExtra("location_name") ?: ""
            val locationAddress = data.getStringExtra("location_address") ?: ""
            val latitude = data.getDoubleExtra("latitude", 0.0)
            val longitude = data.getDoubleExtra("longitude", 0.0)
            
            // 处理地点选择结果（通过可复用的对话框组件）
            if (::eventEditDialogHelper.isInitialized) {
                eventEditDialogHelper.handleLocationResult(locationName, locationAddress, latitude, longitude)
            }
        } else if (requestCode == REQUEST_SETTINGS && resultCode == RESULT_OK) {
            // 从设置页或登录页返回，重新加载所有事件（可能切换了模式）
            updateCloudModeButton()
            
            // 如果登录成功，自动切换到云端模式
            if (PreferenceManager.isLoggedIn(this) && !PreferenceManager.isCloudMode(this)) {
                PreferenceManager.setCloudMode(this, true)
                Toast.makeText(this, "已自动切换到云端模式", Toast.LENGTH_SHORT).show()
            }
            
            loadAllEvents()
            updateCloudModeButton()
        }
    }
    
    companion object {
        private const val REQUEST_SETTINGS = 1002
    }
    
    // 弹出添加日程的对话框
    /**
     * 显示添加/编辑日程对话框（使用可复用的组件）
     * 确保所有视图模式下使用相同的对话框组件和逻辑
     */
    private fun showAddEventDialog(eventToEdit: Event? = null) {
        // 使用可复用的对话框组件，确保所有视图模式统一
        eventEditDialogHelper.show(eventToEdit, selectedDate)
    }
    
    // 从数据库/云端加载所有日程（根据模式自动切换）
    private fun loadAllEvents() {
        // 取消之前的加载操作（避免竞态条件）
        loadEventsJob?.cancel()
        loadEventsJob = lifecycleScope.launch(Dispatchers.IO) {
            loadAllEventsSync()
        }
    }
    
    // 同步加载所有日程（内部方法，不创建新的Job）
    private suspend fun loadAllEventsSync() {
        try {
            val userEvents: List<Event>
            
            // 根据模式获取用户自己的事件
            if (PreferenceManager.isCloudMode(this@MainActivity) && PreferenceManager.isLoggedIn(this@MainActivity)) {
                // 云端模式：从API获取
                val result = eventRepository.getAllEvents()
                userEvents = result.getOrElse { emptyList() }
            } else {
                // 本地模式：从数据库获取
                userEvents = eventDao.getUserEvents()
            }
            
            // 获取订阅的日历事件（订阅始终是本地存储的）
            val subscriptionEvents = subscriptionManager.getVisibleEvents()
                .filter { it.subscriptionId != null } // 只要订阅的事件
            
            // 合并用户事件和订阅事件
            val allEvents = userEvents + subscriptionEvents
            
            withContext(Dispatchers.Main) {
                // 先构建新列表（在内存中，不直接操作 eventsList）
                val newEventsList = allEvents.toMutableList()
                
                // **原子替换：先保存当前选中日期的事件，避免列表闪烁**
                val currentSelectedDate = selectedDate
                val currentDateEvents = if (currentSelectedDate != null) {
                    eventsList.filter { event ->
                        val eventDate = Instant.ofEpochMilli(event.dateTime)
                            .atZone(ZoneId.systemDefault())
                            .toLocalDate()
                        eventDate == currentSelectedDate && event.subscriptionId == null
                    }
                } else {
                    emptyList()
                }
                
                // 一次性替换整个列表（原子操作，避免列表短暂为空）
                eventsList.clear()
                eventsList.addAll(newEventsList)
                
                updateCalendarDots()  // 更新日历标记
                
                // **立即使用新数据更新列表显示（确保不显示空列表）**
                // 根据当前视图模式更新显示
                when (viewMode) {
                    0 -> {
                        // 月视图：如果当前是日程Tab，立即刷新列表显示
                        if (currentTab == 0) {
                            updateEventsList()
                        }
                    }
                    1 -> {
                        // 周视图：更新时间线
                        updateWeekView()
                    }
                    2 -> {
                        // 日视图：更新时间线
                        updateDayView()
                    }
                }
                
                // 刷新周视图日历
                weekCalendarView.notifyCalendarChanged()
            }
        } catch (e: Exception) {
            withContext(Dispatchers.Main) {
                Toast.makeText(this@MainActivity, "加载失败: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }
    
    // 加载指定日期的日程（根据模式自动切换）
    // 注意：这个方法只更新列表显示，不改变 eventsList（用于日历标记）
    private fun loadEventsForSelectedDate(date: Long) {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val userEvents: List<Event>
                
                // 根据模式获取用户自己的事件
                if (PreferenceManager.isCloudMode(this@MainActivity) && PreferenceManager.isLoggedIn(this@MainActivity)) {
                    // 云端模式：从API获取
                    val result = eventRepository.getEventsForDate(date)
                    userEvents = result.getOrElse { emptyList() }
                } else {
                    // 本地模式：从数据库获取
                    userEvents = eventDao.getEventsForDate(date)
                        .filter { it.subscriptionId == null } // 只要用户创建的
                }
                
                // 获取订阅的日历事件（订阅始终是本地存储的）
                val subscriptionEvents = subscriptionManager.getVisibleEvents(date)
                    .filter { it.subscriptionId != null } // 只要订阅的事件
                
                // 合并用户事件和订阅事件
                val allEvents = userEvents + subscriptionEvents
                
                withContext(Dispatchers.Main) {
                    // 确保 eventsList 中包含所有事件（用于日历标记）
                    // 只更新当前日期的事件，不影响其他日期的事件
                    val selected = selectedDate ?: return@withContext
                    
                    // **原子更新：先构建包含新事件的完整列表，再一次性替换（避免闪烁）**
                    // 获取新事件中已有的ID集合（用于去重）
                    val newEventIds = allEvents.map { it.id }.toSet()
                    
                    // **关键修复：先保留当前日期的事件（避免切换日期时列表消失）**
                    // 如果加载的数据为空，但 eventsList 中有当前日期的事件，保留它们
                    val currentDateEventsInList = eventsList.filter { event ->
                        val eventDate = Instant.ofEpochMilli(event.dateTime)
                            .atZone(ZoneId.systemDefault())
                            .toLocalDate()
                        eventDate == selected && event.subscriptionId == null
                    }
                    
                    // 构建新的完整列表（先合并，再替换）
                    val updatedEventsList = eventsList.toMutableList().apply {
                        // **如果加载的数据为空，保留当前日期的事件，不进行任何更新**
                        if (allEvents.isEmpty()) {
                            // 加载的数据为空，保留现有事件（可能是加载失败或确实没有数据）
                            // 不做任何修改，保持当前状态
                        } else {
                            // 加载的数据不为空，进行更新
                            // 先更新已存在的事件（如果有相同ID的新数据，优先使用新数据）
                            allEvents.forEach { newEvent ->
                                val existingIndex = indexOfFirst { it.id == newEvent.id }
                                if (existingIndex >= 0) {
                                    this[existingIndex] = newEvent
                                }
                            }
                            
                            // 移除当前日期的旧事件（只移除不在新事件列表中的）
                            removeAll { event ->
                                val eventDate = Instant.ofEpochMilli(event.dateTime)
                                    .atZone(ZoneId.systemDefault())
                                    .toLocalDate()
                                eventDate == selected && !newEventIds.contains(event.id)
                            }
                            
                            // 添加新事件（只添加不存在的事件，避免重复）
                            val eventsToAdd = allEvents.filter { newEvent ->
                                !any { existingEvent -> existingEvent.id == newEvent.id }
                            }
                            addAll(eventsToAdd)
                        }
                    }
                    
                    // **原子替换：一次性更新整个列表（避免中间状态导致列表闪烁）**
                    eventsList.clear()
                    eventsList.addAll(updatedEventsList)
                    
                    // 同步更新datesWithEvents以便日历标记正确显示
                    allEvents.forEach { event ->
                        val eventDate = Instant.ofEpochMilli(event.dateTime)
                            .atZone(ZoneId.systemDefault())
                            .toLocalDate()
                        if (event.subscriptionId == null) {
                            datesWithEvents.add(eventDate)
                        }
                    }
                    
                    // **立即更新列表显示（确保不显示空列表）**
                    updateEventsList()
                }
            } catch (e: Exception) {
                // 如果加载失败，至少保证列表不消失
                withContext(Dispatchers.Main) {
                    // 不更新列表，保持现有显示
                }
            }
        }
    }
    
    // 添加日程（根据模式自动切换本地/云端）
    private fun addEvent(
        title: String,
        description: String = "",
        dateTime: Long,
        reminderMinutes: Int = 0,
        locationName: String = "",
        latitude: Double = 0.0,
        longitude: Double = 0.0
    ) {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val event = Event(
                    title = title,
                    description = description,
                    dateTime = dateTime,
                    reminderMinutes = reminderMinutes,
                    subscriptionId = null,  // 用户创建的日程
                    locationName = locationName,
                    latitude = latitude,
                    longitude = longitude
                )
                
                // 根据模式创建事件
                val result = eventRepository.createEvent(event)
                val savedEvent = result.getOrElse {
                    withContext(Dispatchers.Main) {
                        Toast.makeText(this@MainActivity, "保存失败: ${it.message}", Toast.LENGTH_SHORT).show()
                    }
                    return@launch
                }
                
                // 设置提醒
                if (reminderMinutes > 0) {
                    withContext(Dispatchers.Main) {
                        val reminderTime = dateTime - (reminderMinutes * 60 * 1000)
                        val currentTime = System.currentTimeMillis()
                        
                        if (reminderTime > currentTime) {
                            // 提醒时间未过，设置提醒并显示
                            reminderManager.setReminder(savedEvent)
                            val df = SimpleDateFormat("HH:mm", Locale.getDefault())
                            Toast.makeText(
                                this@MainActivity,
                                "⏰ 将在 ${df.format(Date(reminderTime))} 提醒您",
                                Toast.LENGTH_LONG
                            ).show()
                        } else {
                            // 提醒时间已过，不设置提醒
                            Toast.makeText(
                                this@MainActivity,
                                "⚠️ 提醒时间已过，无法设置提醒",
                                Toast.LENGTH_SHORT
                            ).show()
                        }
                    }
                }
                
                // 根据事件的日期加载对应日期的事件，如果事件日期与选中日期不同，则切换到事件日期
                val eventDate = Instant.ofEpochMilli(dateTime)
                    .atZone(ZoneId.systemDefault())
                    .toLocalDate()
                
                val eventDateMillis = eventDate.atStartOfDay(ZoneId.systemDefault()).toInstant().toEpochMilli()
                
                // 重新加载所有事件（确保新添加的事件能够显示）
                loadAllEvents()
                
                // 加载事件日期的事件
                loadEventsForSelectedDate(eventDateMillis)
                
                withContext(Dispatchers.Main) {
                    // 如果事件日期与选中日期不同，切换到事件日期
                    if (selectedDate != eventDate) {
                        selectedDate = eventDate
                        updateDateDisplay(eventDate)
                        calendarView.notifyCalendarChanged()
                    }
                    
                    // 更新日历标记（加载所有事件以便更新标记点）
                    updateCalendarDots()
                    
                    // 刷新周视图
                    weekCalendarView.notifyCalendarChanged()
                    Toast.makeText(this@MainActivity, "✅ 添加成功！", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@MainActivity, "保存失败: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
    
    // 更新日程（只能更新用户创建的，根据模式自动切换本地/云端）
    private fun updateEvent(
        id: Long,
        title: String,
        description: String,
        dateTime: Long,
        reminderMinutes: Int = 0,
        locationName: String = "",
        latitude: Double = 0.0,
        longitude: Double = 0.0
    ) {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                // 根据模式获取现有事件
                val existingEvent: Event? = if (PreferenceManager.isCloudMode(this@MainActivity) && PreferenceManager.isLoggedIn(this@MainActivity)) {
                    // 云端模式：从API获取
                    val result = eventRepository.getAllEvents()
                    result.getOrNull()?.find { it.id == id }
                } else {
                    // 本地模式：从数据库获取
                    eventDao.getAllEvents().find { it.id == id }
                }
                
                if (existingEvent == null) {
                    withContext(Dispatchers.Main) {
                        Toast.makeText(this@MainActivity, "日程不存在", Toast.LENGTH_SHORT).show()
                    }
                    return@launch
                }
                
                if (existingEvent.subscriptionId != null) {
                    withContext(Dispatchers.Main) {
                        Toast.makeText(this@MainActivity, "不能编辑订阅的日程", Toast.LENGTH_SHORT).show()
                    }
                    return@launch
                }
                
                // 先取消旧提醒（无论新提醒是否设置）
                withContext(Dispatchers.Main) {
                    reminderManager.cancelReminder(id)
                }
                
                val event = Event(
                    id = id,
                    title = title,
                    description = description,
                    dateTime = dateTime,
                    reminderMinutes = reminderMinutes,
                    subscriptionId = null,  // 保持为null
                    locationName = locationName,
                    latitude = latitude,
                    longitude = longitude
                )
                
                // 根据模式更新事件
                val result = eventRepository.updateEvent(event)
                if (result.isFailure) {
                    withContext(Dispatchers.Main) {
                        Toast.makeText(this@MainActivity, "更新失败: ${result.exceptionOrNull()?.message}", Toast.LENGTH_SHORT).show()
                    }
                    return@launch
                }
                
                // 设置新提醒（如果设置了提醒且提醒时间未过）
                if (reminderMinutes > 0) {
                    withContext(Dispatchers.Main) {
                        val reminderTime = dateTime - (reminderMinutes * 60 * 1000)
                        val currentTime = System.currentTimeMillis()
                        
                        if (reminderTime > currentTime) {
                            // 提醒时间未过，设置提醒并显示
                            reminderManager.setReminder(event)
                            val df = SimpleDateFormat("HH:mm", Locale.getDefault())
                            Toast.makeText(
                                this@MainActivity,
                                "⏰ 将在 ${df.format(Date(reminderTime))} 提醒您",
                                Toast.LENGTH_LONG
                            ).show()
                        } else {
                            // 提醒时间已过，不设置提醒（已取消旧提醒）
                        }
                    }
                }
                // 如果 reminderMinutes == 0，说明不需要提醒，已经取消了旧提醒
                
                // 根据事件的日期加载对应日期的事件
                val eventDate = Instant.ofEpochMilli(dateTime)
                    .atZone(ZoneId.systemDefault())
                    .toLocalDate()
                
                // **立即更新 eventsList 中的事件（避免闪烁）**
                withContext(Dispatchers.Main) {
                    // 更新 eventsList 中的对应事件
                    val index = eventsList.indexOfFirst { it.id == event.id }
                    if (index >= 0) {
                        eventsList[index] = event
                    } else {
                        // 如果不在列表中，添加进去
                        eventsList.add(event)
                    }
                    
                    // 更新日历标记点
                    val oldDate = existingEvent.dateTime.let {
                        Instant.ofEpochMilli(it)
                            .atZone(ZoneId.systemDefault())
                            .toLocalDate()
                    }
                    datesWithEvents.remove(oldDate)
                    datesWithEvents.add(eventDate)
                    
                    // 如果事件日期与选中日期不同，切换到事件日期
                    if (selectedDate != eventDate) {
                        selectedDate = eventDate
                        updateDateDisplay(eventDate)
                        calendarView.notifyCalendarChanged()
                    }
                    
                    // 立即刷新列表显示（确保显示更新后的数据）
                    updateEventsList()
                    
                    // 更新日历标记
                    updateCalendarDots()
                    
                    // 刷新周视图
                    weekCalendarView.notifyCalendarChanged()
                    Toast.makeText(this@MainActivity, "✅ 更新成功！", Toast.LENGTH_SHORT).show()
                }
                
                // 异步重新加载所有事件（确保数据同步）
                loadAllEvents()
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@MainActivity, "更新失败: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
    
    // 更新日程列表显示（只显示选中日期的事件）
    private fun updateEventsList() {
        // 过滤出选中日期的事件，且只显示用户创建的事件（排除订阅的）
        val selected = selectedDate ?: return
        
        val filteredEvents = eventsList.filter { event ->
            val eventDate = Instant.ofEpochMilli(event.dateTime)
                .atZone(ZoneId.systemDefault())
                .toLocalDate()
            // 只显示用户创建的日程（subscriptionId == null）
            eventDate == selected && event.subscriptionId == null
        }
        
        adapter.updateEvents(filteredEvents)
    }
    
    // 显示日程详情
    private fun showEventDetails(event: Event) {
        val dateFormat = SimpleDateFormat("yyyy年MM月dd日 EEEE HH:mm", Locale.CHINESE)
        val dateStr = dateFormat.format(Date(event.dateTime))
        
        // 获取订阅信息（同步获取）
        var subscriptionName: String? = null
        if (event.subscriptionId != null) {
            lifecycleScope.launch(Dispatchers.IO) {
                try {
                    val subscription = subscriptionDao.getAllSubscriptions().find { it.id == event.subscriptionId }
                    subscriptionName = subscription?.name
        
        // 获取农历信息
        getLunarDate(event.dateTime) { lunar ->
                        val message = buildString {
                            append("📅 日期：$dateStr\n\n")
                            append("📝 标题：${event.title}\n\n")
                            if (event.description.isNotEmpty()) {
                                append("💬 描述：${event.description}\n\n")
                            }
                            if (subscriptionName != null) {
                                append("📡 来源：$subscriptionName\n\n")
                            }
                            if (lunar.isNotEmpty()) {
                                append("🏮 农历：$lunar")
                            }
                        }
                        
                        val builder = AlertDialog.Builder(this@MainActivity)
                            .setTitle("📋 日程详情")
                            .setMessage(message)
                            .setNeutralButton("关闭", null)
                        
                        // 只有用户创建的日程才能编辑和删除
                        if (event.subscriptionId == null) {
                            builder.setPositiveButton("编辑") { _, _ ->
                                showAddEventDialog(event)
                            }
                            builder.setNegativeButton("删除") { _, _ ->
                                showDeleteConfirmDialog(event)
                            }
                        }
                        
                        builder.show()
                    }
                } catch (e: Exception) {
                    // 如果获取订阅信息失败，直接显示
                    showEventDetailsWithoutSubscription(event, dateStr)
                }
            }
        } else {
            // 用户创建的日程，直接显示
            getLunarDate(event.dateTime) { lunar ->
            val message = buildString {
                append("📅 日期：$dateStr\n\n")
                append("📝 标题：${event.title}\n\n")
                if (event.description.isNotEmpty()) {
                    append("💬 描述：${event.description}\n\n")
                }
                    if (lunar.isNotEmpty()) {
                        append("🏮 农历：$lunar")
                }
            }
            
            AlertDialog.Builder(this)
                .setTitle("📋 日程详情")
                .setMessage(message)
                .setPositiveButton("编辑") { _, _ ->
                    showAddEventDialog(event)
                }
                .setNegativeButton("删除") { _, _ ->
                        showDeleteConfirmDialog(event)
                }
                .setNeutralButton("关闭", null)
                .show()
            }
        }
    }
    
    // 显示日程详情（无订阅信息版本）
    private fun showEventDetailsWithoutSubscription(event: Event, dateStr: String) {
        val message = buildString {
            append("📅 日期：$dateStr\n\n")
            append("📝 标题：${event.title}\n\n")
            if (event.description.isNotEmpty()) {
                append("💬 描述：${event.description}\n\n")
            }
        }
        
        val builder = AlertDialog.Builder(this)
            .setTitle("📋 日程详情")
            .setMessage(message)
            .setNeutralButton("关闭", null)
        
        if (event.subscriptionId == null) {
            builder.setPositiveButton("编辑") { _, _ ->
                showAddEventDialog(event)
            }
            builder.setNegativeButton("删除") { _, _ ->
                showDeleteConfirmDialog(event)
            }
        }
        
        builder.show()
    }
    
    // 显示删除确认对话框
    private fun showDeleteConfirmDialog(event: Event) {
        AlertDialog.Builder(this)
            .setTitle("🗑️ 删除日程")
            .setMessage("确定要删除「${event.title}」吗？")
            .setPositiveButton("删除") { _, _ ->
                deleteEvent(event)
            }
            .setNegativeButton("取消", null)
            .show()
    }
    
    // 删除日程（只能删除用户创建的，不能删除订阅的，根据模式自动切换本地/云端）
    private fun deleteEvent(event: Event) {
        // 检查是否是订阅的事件
        if (event.subscriptionId != null) {
            Toast.makeText(this, "不能删除订阅的日程，请在订阅管理中取消订阅", Toast.LENGTH_LONG).show()
            return
        }
        
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                // 取消提醒
                withContext(Dispatchers.Main) {
                    reminderManager.cancelReminder(event.id)
                }
                
                // 根据模式删除事件
                val result = eventRepository.deleteEvent(event)
                if (result.isFailure) {
                    withContext(Dispatchers.Main) {
                        Toast.makeText(this@MainActivity, "删除失败: ${result.exceptionOrNull()?.message}", Toast.LENGTH_SHORT).show()
                    }
                    return@launch
                }
                
                // 立即从列表中移除，让UI立即更新
                withContext(Dispatchers.Main) {
                    // 从 eventsList 中移除删除的事件
                    eventsList.removeAll { it.id == event.id }
                    
                    // 从 datesWithEvents 中移除对应的日期（如果该日期没有其他事件）
                    val eventDate = Instant.ofEpochMilli(event.dateTime)
                        .atZone(ZoneId.systemDefault())
                        .toLocalDate()
                    val hasOtherEventsOnDate = eventsList.any { e ->
                        val eDate = Instant.ofEpochMilli(e.dateTime)
                            .atZone(ZoneId.systemDefault())
                            .toLocalDate()
                        eDate == eventDate && e.subscriptionId == null
                    }
                    if (!hasOtherEventsOnDate) {
                        datesWithEvents.remove(eventDate)
                    }
                    
                    // 立即更新UI（让用户立即看到删除效果）
                    updateEventsList()
                    
                    // 根据当前视图模式更新相应的时间线
                    when (viewMode) {
                        1 -> {
                            // 周视图：立即更新时间线
                            updateWeekView()
                        }
                        2 -> {
                            // 日视图：立即更新时间线
                            updateDayView()
                        }
                    }
                    
                    // 刷新周视图日历
                    weekCalendarView.notifyCalendarChanged()
                    
                    // 刷新日历视图
                    calendarView.notifyCalendarChanged()
                    
                    Toast.makeText(this@MainActivity, "🗑️ 删除成功！", Toast.LENGTH_SHORT).show()
                }
                
                // 异步刷新完整数据（确保数据一致性）
                selectedDate?.let { 
                    val millis = it.atStartOfDay(ZoneId.systemDefault()).toInstant().toEpochMilli()
                    loadEventsForSelectedDate(millis)
                }
                updateCalendarDots()  // 更新日历标记
                
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@MainActivity, "删除失败: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
    
    // ==================== 网络功能 ====================
    // 订阅功能已移至 SubscriptionsActivity
    
    /**
     * 获取农历日期（在日程详情显示）
     */
    private fun getLunarDate(dateTime: Long, callback: (String) -> Unit) {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val dateFormat = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
                val dateStr = dateFormat.format(Date(dateTime))
                
                // 调用后端 API
                val lunar = RetrofitClient.api.getLunarDate(dateStr)
                
                withContext(Dispatchers.Main) {
                    callback("${lunar.lunar_date} ${lunar.zodiac}年")
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    callback("")  // 失败就不显示
                }
            }
        }
    }
    
    // ==================== Tab 切换功能 ====================
    
    /**
     * 切换显示的内容区域
     */
    private fun switchContent(tabIndex: Int) {
        when (tabIndex) {
            0 -> {
                // 日程安排：只切换显示，不在这里刷新列表
                // 列表刷新由 Tab 切换逻辑统一处理，避免重复调用
                recyclerView.visibility = android.view.View.VISIBLE
                scrollViewHoliday.visibility = android.view.View.GONE
                scrollViewFortune.visibility = android.view.View.GONE
            }
            1 -> {
                // 今日节日
                recyclerView.visibility = android.view.View.GONE
                scrollViewHoliday.visibility = android.view.View.VISIBLE
                scrollViewFortune.visibility = android.view.View.GONE
            }
            2 -> {
                // 今日运势
                recyclerView.visibility = android.view.View.GONE
                scrollViewHoliday.visibility = android.view.View.GONE
                scrollViewFortune.visibility = android.view.View.VISIBLE
            }
        }
    }
    
    /**
     * 根据当前选中的 Tab 加载数据
     */
    private fun loadDataForSelectedDate(date: Long) {
        when (currentTab) {
            0 -> {
                // 加载日程
                loadEventsForSelectedDate(date)
            }
            1 -> {
                // 加载节日信息
                loadHolidayInfo(date)
            }
            2 -> {
                // ✅ 使用 FortuneManager 加载今日运势（结合天气）
                fortuneManager.loadFortune(
                    weatherManager.currentWeather,
                    weatherManager.currentTemperature
                )
            }
        }
    }
    
    /**
     * 加载节日信息（合并API节日 + 订阅的节日）
     */
    private fun loadHolidayInfo(date: Long) {
        // ✅ 使用 HolidayManager 处理节日信息加载
        // 注意：HolidayManager内部会使用subscriptionManager.getVisibleEvents()来获取有效订阅事件
        holidayManager.loadHolidayInfo(date, lifecycleScope)
        
        // 更新日历上的节日标记（确保订阅的节日在日历上显示）
        updateCalendarDots()
    }
    
    // ✅ loadWeather() 已被 WeatherManager 替代，位于 ui/managers/WeatherManager.kt
    
    // ✅ addFestivalCard() 已被 HolidayManager 替代，位于 ui/managers/HolidayManager.kt
    
    // ==================== 日历设置和辅助方法 ====================
    
    /**
     * 初始化日历
     */
    private fun setupCalendar() {
        // 设置日历显示范围：当前月份前后各6个月
        val startMonth = YearMonth.now().minusMonths(6)
        val endMonth = YearMonth.now().plusMonths(6)
        val firstDayOfWeek = daysOfWeek().first()  // 周日为第一天
        
        calendarView.setup(startMonth, endMonth, firstDayOfWeek)
        calendarView.scrollToMonth(currentMonth)
        
        // 设置日期绑定器
        calendarView.dayBinder = object : MonthDayBinder<DayViewContainer> {
            override fun create(view: View) = DayViewContainer(view)
            
            override fun bind(container: DayViewContainer, data: CalendarDay) {
                container.day = data
                val textView = container.textView
                val dotView = container.dotView
                val festivalLabel = container.festivalLabel
                
                textView.text = data.date.dayOfMonth.toString()
                
                // 根据日期位置设置样式
                when (data.position) {
                    DayPosition.MonthDate -> {
                        textView.visibility = View.VISIBLE
                        
                        // 设置日期背景和颜色
                        when {
                            // 选中的日期
                            selectedDate == data.date -> {
                                textView.setBackgroundResource(R.drawable.calendar_day_selected)
                                textView.setTextColor(getColor(android.R.color.white))
                            }
                            // 今天
                            data.date == LocalDate.now() -> {
                                textView.setBackgroundResource(R.drawable.calendar_day_today)
                                textView.setTextColor(getColor(R.color.purple_500))
                            }
                            // 普通日期
                            else -> {
                                textView.background = null
                                textView.setTextColor(getColor(R.color.black))
                            }
                        }
                        
                        // 显示节日名称（有节日的日期）
                        val festivalName = datesWithFestivals[data.date]
                        if (festivalName != null) {
                            festivalLabel.text = festivalName
                            festivalLabel.visibility = View.VISIBLE
                        } else {
                            festivalLabel.visibility = View.GONE
                        }
                        
                        // 显示标记点（有用户日程的日期）
                        dotView.visibility = if (datesWithEvents.contains(data.date)) {
                            View.VISIBLE
                        } else {
                            View.GONE
                        }
                    }
                    else -> {
                        // 不属于当前月份的日期
                        textView.visibility = View.INVISIBLE
                        dotView.visibility = View.GONE
                        festivalLabel.visibility = View.GONE
                    }
                }
            }
        }
        
        // 设置月份滚动监听
        calendarView.monthScrollListener = object : MonthScrollListener {
            override fun invoke(month: CalendarMonth) {
                currentMonth = month.yearMonth
                updateMonthYearDisplay(currentMonth)
            }
        }
        
        // 更新月份显示
        updateMonthYearDisplay(currentMonth)
    }
    
    /**
     * 初始化周视图
     */
    private fun setupWeekCalendar() {
        val startWeek = LocalDate.now().minusWeeks(52)
        val endWeek = LocalDate.now().plusWeeks(52)
        val firstDayOfWeek = daysOfWeek().first()
        
        weekCalendarView.setup(startWeek, endWeek, firstDayOfWeek)
        weekCalendarView.scrollToWeek(LocalDate.now())
        
        // 设置周视图绑定器
        weekCalendarView.dayBinder = object : WeekDayBinder<WeekDayViewContainer> {
            override fun create(view: View) = WeekDayViewContainer(view)
            
            override fun bind(container: WeekDayViewContainer, data: com.kizitonwose.calendar.core.WeekDay) {
                container.day = data
                
                // 设置星期几
                val dayOfWeekMap = mapOf(
                    java.time.DayOfWeek.MONDAY to "周一",
                    java.time.DayOfWeek.TUESDAY to "周二",
                    java.time.DayOfWeek.WEDNESDAY to "周三",
                    java.time.DayOfWeek.THURSDAY to "周四",
                    java.time.DayOfWeek.FRIDAY to "周五",
                    java.time.DayOfWeek.SATURDAY to "周六",
                    java.time.DayOfWeek.SUNDAY to "周日"
                )
                val weekDayText = dayOfWeekMap[data.date.dayOfWeek] ?: "?"
                container.dayText.text = weekDayText
                container.dayText.visibility = View.VISIBLE
                container.numberText.text = data.date.dayOfMonth.toString()
                
                // 设置样式（先设置默认样式，再设置特殊样式）
                if (selectedDate == data.date) {
                    // 选中日期
                    container.numberText.setPadding(0, 0, 0, 0)
                    container.numberText.setBackgroundResource(R.drawable.calendar_day_selected)
                    container.numberText.setTextColor(getColor(android.R.color.white))
                } else if (data.date == LocalDate.now()) {
                    // 今天
                    container.numberText.setPadding(0, 0, 0, 0)
                    container.numberText.setBackgroundResource(R.drawable.calendar_day_today)
                    container.numberText.setTextColor(getColor(R.color.purple_500))
                } else {
                    // 普通日期
                    container.numberText.setPadding(0, 0, 0, 0)
                    container.numberText.background = null
                    container.numberText.setTextColor(getColor(R.color.black))
                }
                
                // 显示节日名称（有节日的日期）
                val festivalName = datesWithFestivals[data.date]
                if (festivalName != null) {
                    container.festivalLabel.text = festivalName
                    container.festivalLabel.visibility = View.VISIBLE
                } else {
                    container.festivalLabel.visibility = View.GONE
                }
                
                // 显示标记点（有用户日程的日期）
                container.dotView.visibility = if (datesWithEvents.contains(data.date)) {
                    View.VISIBLE
                } else {
                    View.GONE
                }
            }
        }
        
        // 周视图滚动监听
        weekCalendarView.weekScrollListener = { week ->
            updateMonthYearDisplay(YearMonth.from(week.days.first().date))
        }
    }
    
    /**
     * 切换视图模式（0=月 1=周 2=日）
     */
    private fun switchViewMode(mode: Int) {
        when (mode) {
            0 -> {
                // 月视图：显示整月日历 + 下方Tab + 天气
                monthViewCard.visibility = View.VISIBLE
                weekViewContainer.visibility = View.GONE
                dayViewCard.visibility = View.GONE
                bottomContentCard.visibility = View.VISIBLE
                weatherCard.visibility = View.VISIBLE
                tvSelectedDate.visibility = View.VISIBLE
                btnViewSwitch.text = "📅 月"
                
                // 滚动到选中日期所在的月份
                selectedDate?.let { 
                    val yearMonth = YearMonth.from(it)
                    currentMonth = yearMonth
                    calendarView.scrollToMonth(yearMonth)
                }
                
                // 恢复Tab内容
                switchContent(currentTab)
                
                // 重新加载所有事件并刷新显示
                loadAllEvents()
            }
            1 -> {
                // 周视图：横向7天选择器 + 时间线（不显示底部内容和天气）
                monthViewCard.visibility = View.GONE
                weekViewContainer.visibility = View.VISIBLE
                dayViewCard.visibility = View.GONE
                bottomContentCard.visibility = View.GONE
                weatherCard.visibility = View.GONE
                tvSelectedDate.visibility = View.VISIBLE
                btnViewSwitch.text = "📅 周"
                
                // 滚动到选中日期所在的周
                selectedDate?.let { weekCalendarView.scrollToWeek(it) }
                
                // 重新加载所有事件并更新时间线
                loadAllEvents()
            }
            2 -> {
                // 日视图：只显示时间线（不显示底部内容和天气）
                monthViewCard.visibility = View.GONE
                weekViewContainer.visibility = View.GONE
                dayViewCard.visibility = View.VISIBLE
                bottomContentCard.visibility = View.GONE
                weatherCard.visibility = View.GONE
                tvSelectedDate.visibility = View.VISIBLE
                btnViewSwitch.text = "📅 日"
                
                // 重新加载所有事件并更新时间线
                loadAllEvents()
            }
        }
    }
    
    /**
     * 选择日期
     */
    private fun selectDate(date: LocalDate) {
        if (selectedDate != date) {
            val oldDate = selectedDate
            selectedDate = date
            
            // 更新月视图的显示
            oldDate?.let { calendarView.notifyDateChanged(it) }
            calendarView.notifyDateChanged(date)
            
            // 刷新整个周视图（确保旧的选中状态被清除）
            weekCalendarView.notifyCalendarChanged()
            
            // 更新显示
            updateDateDisplay(date)
            
            // **立即使用已有数据更新列表显示**（避免切换时列表为空）
            updateEventsList()
            
            // 转换日期为毫秒
            val millis = date.atStartOfDay(ZoneId.systemDefault()).toInstant().toEpochMilli()
            
            // **始终加载节日数据**（无论当前在哪个视图和Tab）
            // 这样切换日期后，用户点击"今日节日"Tab时能立即看到最新数据
            loadHolidayInfo(millis)
            
            // 根据当前视图模式加载其他数据
            when (viewMode) {
                0 -> {
                    // 月视图：加载当前日期的日程到eventsList并显示在底部
                    loadEventsForSelectedDate(millis)
                }
                1 -> {
                    // 周视图：如果eventsList为空，需要加载所有事件
                    // 否则直接更新时间线显示（loadAllEvents已在切换视图时调用）
                    if (eventsList.isEmpty()) {
                        loadAllEvents()
                    } else {
                        updateWeekView()
                    }
                }
                2 -> {
                    // 日视图：如果eventsList为空，需要加载所有事件
                    // 否则直接更新时间线显示（loadAllEvents已在切换视图时调用）
                    if (eventsList.isEmpty()) {
                        loadAllEvents()
                    } else {
                        updateDayView()
                    }
                }
            }
        }
    }
    
    /**
     * 更新选中日期的显示
     */
    private fun updateDateDisplay(date: LocalDate) {
        val formatter = DateTimeFormatter.ofPattern("yyyy年MM月dd日 EEEE", Locale.CHINESE)
        tvSelectedDate.text = "选中日期: ${date.format(formatter)}"
    }
    
    /**
     * 更新月份年份显示
     */
    private fun updateMonthYearDisplay(yearMonth: YearMonth) {
        val formatter = DateTimeFormatter.ofPattern("yyyy年MM月", Locale.CHINESE)
        tvMonthYear.text = yearMonth.format(formatter)
    }
    
    /**
     * 加载指定日期的数据（根据当前Tab）
     */
    private fun loadDataForDate(date: LocalDate) {
        // 转换 LocalDate 到 Long (毫秒)
        val millis = date.atStartOfDay(ZoneId.systemDefault()).toInstant().toEpochMilli()
        
        when (currentTab) {
            0 -> loadEventsForSelectedDate(millis)
            1 -> loadHolidayInfo(millis)
            2 -> {
                // ✅ 使用 FortuneManager 加载今日运势（结合天气）
                fortuneManager.loadFortune(
                    weatherManager.currentWeather,
                    weatherManager.currentTemperature
                )
            }
        }
    }
    
    /**
     * 更新日历上的标记点（显示哪些日期有日程）
     */
    private fun updateCalendarDots() {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                // 根据模式获取用户自己的事件
                val userEvents: List<Event>
                if (PreferenceManager.isCloudMode(this@MainActivity) && PreferenceManager.isLoggedIn(this@MainActivity)) {
                    // 云端模式：从API获取
                    val result = eventRepository.getAllEvents()
                    userEvents = result.getOrElse { emptyList() }
                } else {
                    // 本地模式：从数据库获取
                    userEvents = eventDao.getUserEvents()
                }
                
                // 获取订阅的日历事件（订阅始终是本地存储的）
                val festivalEvents = subscriptionManager.getVisibleEvents()
                    .filter { it.subscriptionId != null }
                
                // 获取已订阅的节日（从FestivalSubscriptionManager）
                val festivalSubscriptionManager = com.ncu.kotlincalendar.data.managers.FestivalSubscriptionManager(this@MainActivity)
                val subscribedFestivalNames = festivalSubscriptionManager.getSubscribedFestivals()
                
                // 转换为 LocalDate 集合
                val newDatesWithEvents = userEvents.map { event ->
                    Instant.ofEpochMilli(event.dateTime)
                        .atZone(ZoneId.systemDefault())
                        .toLocalDate()
                }.toSet()
                
                // 1. 从订阅的公共日历事件中获取节日日期
                val festivalDatesFromEvents = festivalEvents.associate { event ->
                    val date = Instant.ofEpochMilli(event.dateTime)
                        .atZone(ZoneId.systemDefault())
                        .toLocalDate()
                    // 提取节日名称（保留emoji）
                    val title = event.title.trim()
                    val emojiMatch = Regex("[\\u{1F300}-\\u{1F9FF}]|[\\u{2600}-\\u{26FF}]|[\\u{2700}-\\u{27BF}]|\\p{So}").find(title)
                    val emoji = emojiMatch?.value ?: ""
                    val nameWithoutEmoji = title.replace(Regex("[\\u{1F300}-\\u{1F9FF}]|[\\u{2600}-\\u{26FF}]|[\\u{2700}-\\u{27BF}]|\\p{So}"), "").trim()
                    val displayName = if (nameWithoutEmoji.length > 4) nameWithoutEmoji.take(4) else nameWithoutEmoji
                    val finalName = if (emoji.isNotEmpty()) "$emoji $displayName" else displayName
                    date to finalName
                }.toMutableMap()
                
                // 2. 从当前可见月份前后各1个月查询API，获取已订阅节日的日期
                val visibleMonth = this@MainActivity.currentMonth  // 使用当前日历显示的月份
                val monthsToCheck = (-1..1).map { visibleMonth.plusMonths(it.toLong()) }
                
                monthsToCheck.forEach { yearMonth ->
                    try {
                        val year = yearMonth.year
                        val month = yearMonth.monthValue
                        // 查询这个月的每一天，检查是否有已订阅的节日
                        val daysInMonth = yearMonth.lengthOfMonth()
                        for (day in 1..daysInMonth) {
                            try {
                                val dateStr = String.format("%04d-%02d-%02d", year, month, day)
                                val holidayResponse = RetrofitClient.api.checkHoliday(dateStr)
                                
                                // 检查API返回的节日是否已订阅
                                holidayResponse.festivals?.forEach { festival ->
                                    if (subscribedFestivalNames.any { subscribedName ->
                                        festival.name == subscribedName ||
                                        festival.name.contains(subscribedName, ignoreCase = true) ||
                                        subscribedName.contains(festival.name, ignoreCase = true) ||
                                        festival.name.split("/")[0].trim() == subscribedName.split("/")[0].trim()
                                    }) {
                                        val festivalDate = LocalDate.of(year, month, day)
                                        val displayName = if (festival.name.length > 4) festival.name.take(4) else festival.name
                                        val finalName = "${festival.emoji} $displayName"
                                        festivalDatesFromEvents[festivalDate] = finalName
                                    }
                                }
                            } catch (e: Exception) {
                                // 忽略单日查询失败，继续查询其他日期
                            }
                        }
                    } catch (e: Exception) {
                        // 忽略单月查询失败，继续查询其他月份
                    }
                }
                
                val newDatesWithFestivals = festivalDatesFromEvents
                
                festivalEvents.forEach { event ->
                    val date = Instant.ofEpochMilli(event.dateTime)
                        .atZone(ZoneId.systemDefault())
                        .toLocalDate()
                }
                
                withContext(Dispatchers.Main) {
                    datesWithEvents.clear()
                    datesWithEvents.addAll(newDatesWithEvents)
                    
                    datesWithFestivals.clear()
                    datesWithFestivals.putAll(newDatesWithFestivals)
                    
                    // 刷新日历显示
                    calendarView.notifyCalendarChanged()
                    weekCalendarView.notifyCalendarChanged()
                }
            } catch (e: Exception) {
            }
        }
    }
    
    /**
     * 更新周视图时间线
     */
    private fun updateWeekView() {
        val selected = selectedDate ?: LocalDate.now()
        
        val filteredEvents = eventsList.filter { event ->
            val eventDate = Instant.ofEpochMilli(event.dateTime)
                .atZone(ZoneId.systemDefault())
                .toLocalDate()
            eventDate == selected
        }
        
        weekTimelineAdapter.updateEvents(filteredEvents)
    }
    
    /**
     * 更新日视图（时间线）
     */
    private fun updateDayView() {
        // 过滤出选中日期的事件
        val selected = selectedDate ?: return
        
        val filteredEvents = eventsList.filter { event ->
            val eventDate = Instant.ofEpochMilli(event.dateTime)
                .atZone(ZoneId.systemDefault())
                .toLocalDate()
            eventDate == selected
        }
        
        dayViewAdapter.updateEvents(filteredEvents)
    }
    
    /**
     * 打开节日详情页面
     */
    private fun openFestivalDetail(name: String, emoji: String, date: String) {
        val intent = android.content.Intent(this, FestivalDetailActivity::class.java).apply {
            putExtra("festival_name", name)
            putExtra("festival_emoji", emoji)
            putExtra("date", date)
        }
        startActivity(intent)
    }
    
    /**
     * 显示添加日程对话框（传统方式）
     * 调用可复用的对话框组件
     */
    private fun showAddEventDialog() {
        // 使用可复用的对话框组件，传入null表示新建日程
        showAddEventDialog(null)
    }
    
    /**
     * 显示AI创建日程对话框
     */
    private fun showAIEventDialog() {
        val dialogView = layoutInflater.inflate(R.layout.dialog_ai_event, null)
        val dialog = AlertDialog.Builder(this)
            .setView(dialogView)
            .create()
        
        // 获取视图元素
        val etAIInput = dialogView.findViewById<TextInputEditText>(R.id.etAIInput)
        val llParsedResult = dialogView.findViewById<LinearLayout>(R.id.llParsedResult)
        val llLoading = dialogView.findViewById<LinearLayout>(R.id.llLoading)
        val tvError = dialogView.findViewById<TextView>(R.id.tvError)
        val btnCancel = dialogView.findViewById<Button>(R.id.btnCancel)
        val btnParse = dialogView.findViewById<Button>(R.id.btnParse)
        val btnConfirm = dialogView.findViewById<Button>(R.id.btnConfirm)
        
        val tvParsedTitle = dialogView.findViewById<TextView>(R.id.tvParsedTitle)
        val tvParsedDate = dialogView.findViewById<TextView>(R.id.tvParsedDate)
        val tvParsedTime = dialogView.findViewById<TextView>(R.id.tvParsedTime)
        val tvParsedDesc = dialogView.findViewById<TextView>(R.id.tvParsedDesc)
        val llParsedTime = dialogView.findViewById<LinearLayout>(R.id.llParsedTime)
        val llParsedDesc = dialogView.findViewById<LinearLayout>(R.id.llParsedDesc)
        
        var parsedEventData: com.ncu.kotlincalendar.api.models.ParsedEvent? = null
        
        // 取消按钮
        btnCancel.setOnClickListener {
            dialog.dismiss()
        }
        
        // AI解析按钮
        btnParse.setOnClickListener {
            val userInput = etAIInput.text.toString().trim()
            
            if (userInput.isEmpty()) {
                Toast.makeText(this, "请输入日程描述", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            
            // 显示加载状态
            llLoading.visibility = View.VISIBLE
            llParsedResult.visibility = View.GONE
            tvError.visibility = View.GONE
            btnParse.isEnabled = false
            
            // 调用AI接口
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                    val request = com.ncu.kotlincalendar.api.models.ParseEventRequest(userInput)
                    val response = RetrofitClient.api.parseEventFromText(request)
                
                withContext(Dispatchers.Main) {
                        llLoading.visibility = View.GONE
                        btnParse.isEnabled = true
                        
                        if (response.success && response.event != null) {
                            // 解析成功
                            val event = response.event
                            parsedEventData = event
                            
                            tvParsedTitle.text = event.title
                            tvParsedDate.text = event.date
                            
                            if (event.time != null) {
                                tvParsedTime.text = event.time
                                llParsedTime.visibility = View.VISIBLE
                            } else {
                                llParsedTime.visibility = View.GONE
                            }
                            
                            // AI解析不需要显示描述
                            llParsedDesc.visibility = View.GONE
                            
                            // 显示解析结果
                            llParsedResult.visibility = View.VISIBLE
                            btnParse.visibility = View.GONE
                            btnConfirm.visibility = View.VISIBLE
                            
                            // 确保按钮可见（延迟执行以等待布局完成）
                            dialogView.postDelayed({
                                btnConfirm.requestFocus()
                                // 滚动到底部
                                val scrollView = dialogView.parent as? android.widget.ScrollView
                                scrollView?.fullScroll(View.FOCUS_DOWN)
                            }, 100)
                            
                        } else {
                            // 解析失败
                            tvError.text = response.error ?: "AI解析失败，请尝试更清晰的描述"
                            tvError.visibility = View.VISIBLE
                        }
                    }
                    
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                        llLoading.visibility = View.GONE
                        btnParse.isEnabled = true
                        tvError.text = "网络错误：${e.message}"
                        tvError.visibility = View.VISIBLE
                    }
                }
            }
        }
        
        // 确认创建按钮
        btnConfirm.setOnClickListener {
            val eventData = parsedEventData
            if (eventData == null) {
                Toast.makeText(this, "没有解析结果", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            
            // 禁用按钮，防止重复点击
            btnConfirm.isEnabled = false
            
            lifecycleScope.launch(Dispatchers.IO) {
                try {
                    // 构建事件数据（只使用标题、日期和时间）
                    val title = eventData.title
                    val date = eventData.date
                    val time = eventData.time
                    
                    // 解析日期时间（本地时区）
                    val dateTimeMillis = try {
                        // 解析日期 YYYY-MM-DD
                        val dateParts = date.split("-")
                        if (dateParts.size != 3) {
                            throw IllegalArgumentException("日期格式错误: $date")
                        }
                        val year = dateParts[0].toInt()
                        val month = dateParts[1].toInt()
                        val day = dateParts[2].toInt()
                        
                        // 解析时间 HH:MM（如果没有时间，默认9点）
                        val hour: Int
                        val minute: Int
                        if (time != null && time.matches(Regex("\\d{2}:\\d{2}"))) {
                            val timeParts = time.split(":")
                            hour = timeParts[0].toInt()
                            minute = timeParts[1].toInt()
                        } else {
                            hour = 9
                            minute = 0
                        }
                        
                        // 使用LocalDateTime转换为时间戳
                        val localDateTime = java.time.LocalDateTime.of(year, month, day, hour, minute)
                        localDateTime.atZone(ZoneId.systemDefault()).toInstant().toEpochMilli()
                    } catch (e: Exception) {
                        withContext(Dispatchers.Main) {
                            btnConfirm.isEnabled = true
                            Log.e("MainActivity", "日期时间解析失败", e)
                            Toast.makeText(
                                this@MainActivity, 
                                "日期时间格式错误：${e.message}", 
                                Toast.LENGTH_LONG
                            ).show()
                        }
                        return@launch
                    }
                    
                    // 创建Event对象（不需要描述和提醒）
                    val event = Event(
                        id = 0,  // 新事件ID为0
                        title = title,
                        description = "",  // AI解析不需要描述
                        dateTime = dateTimeMillis,
                        reminderMinutes = 0,  // AI解析不需要提醒
                        subscriptionId = null,  // 用户创建的日程
                        locationName = "",
                        latitude = 0.0,
                        longitude = 0.0
                    )
                    
                    // 保存到本地数据库
                    val eventId = eventDao.insert(event)
                    val savedEvent = event.copy(id = eventId)
                    
                    // AI解析不需要设置提醒
                    withContext(Dispatchers.Main) {
                        
                        // 立即将新事件添加到 eventsList（用于立即显示）
                        eventsList.add(savedEvent)
                        
                        // 更新日历标记点
                        val eventDate = Instant.ofEpochMilli(savedEvent.dateTime)
                            .atZone(ZoneId.systemDefault())
                            .toLocalDate()
                        datesWithEvents.add(eventDate)
                        
                        // 立即刷新列表显示（如果创建的是当前选中日期的事件）
                        val selected = selectedDate
                        if (selected != null && eventDate == selected) {
                            updateEventsList()
                        }
                        
                        // 更新日历标记
                        updateCalendarDots()
                        
                        Toast.makeText(this@MainActivity, "✅ 日程创建成功！", Toast.LENGTH_SHORT).show()
                        dialog.dismiss()
                    }
                    
                    // 异步重新加载所有事件（确保数据同步）
                    loadAllEvents()
                } catch (e: Exception) {
                    withContext(Dispatchers.Main) {
                        btnConfirm.isEnabled = true
                        Log.e("MainActivity", "AI创建日程失败", e)
                        Toast.makeText(
                            this@MainActivity, 
                            "创建失败：${e.message ?: "未知错误"}", 
                            Toast.LENGTH_LONG
                        ).show()
                    }
                }
            }
        }
        
        dialog.show()
    }
    
    /**
     * 切换云端/本地模式
     */
    private fun toggleCloudMode() {
        val isCurrentlyCloud = PreferenceManager.isCloudMode(this)
        
        if (isCurrentlyCloud) {
            // 当前是云端模式，切换到本地
            AlertDialog.Builder(this)
                .setTitle("切换到本地模式")
                .setMessage("切换后将使用本地数据，云端数据不会同步。确定切换吗？")
                .setPositiveButton("确定") { _, _ ->
                    PreferenceManager.setCloudMode(this, false)
                    updateCloudModeButton()
                    loadAllEvents()
                    Toast.makeText(this, "已切换到本地模式", Toast.LENGTH_SHORT).show()
                }
                .setNegativeButton("取消", null)
                .show()
        } else {
            // 当前是本地模式，切换到云端
            if (!PreferenceManager.isLoggedIn(this)) {
                // 未登录，需要先登录
                AlertDialog.Builder(this)
                    .setTitle("需要登录")
                    .setMessage("云端模式需要登录账号。是否前往登录？")
                    .setPositiveButton("去登录") { _, _ ->
                        val intent = Intent(this, LoginActivity::class.java)
                        startActivityForResult(intent, REQUEST_SETTINGS)
                    }
                    .setNegativeButton("取消", null)
                    .show()
            } else {
                // 已登录，直接切换
                AlertDialog.Builder(this)
                    .setTitle("切换到云端模式")
                    .setMessage("切换后将使用云端数据并同步到服务器。确定切换吗？")
                    .setPositiveButton("确定") { _, _ ->
                        PreferenceManager.setCloudMode(this, true)
                        updateCloudModeButton()
                        loadAllEvents()
                        Toast.makeText(this, "已切换到云端模式", Toast.LENGTH_SHORT).show()
                    }
                    .setNegativeButton("取消", null)
                    .show()
            }
        }
    }
    
    /**
     * 更新云端模式按钮的显示状态
     */
    private fun updateCloudModeButton() {
        val isCloudMode = PreferenceManager.isCloudMode(this)
        val isLoggedIn = PreferenceManager.isLoggedIn(this)
        
        if (isCloudMode && isLoggedIn) {
            btnCloudMode.text = "☁️\n云端"
            btnCloudMode.setBackgroundColor(ContextCompat.getColor(this, android.R.color.holo_blue_light))
        } else {
            btnCloudMode.text = "📱\n本地"
            btnCloudMode.setBackgroundColor(ContextCompat.getColor(this, android.R.color.darker_gray))
        }
    }
}
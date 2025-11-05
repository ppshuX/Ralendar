package com.ncu.kotlincalendar

import android.os.Bundle
import android.widget.Button
import android.widget.CalendarView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.text.SimpleDateFormat
import java.util.*

class MainActivity : AppCompatActivity() {
    
    private lateinit var calendarView: CalendarView
    private lateinit var tvSelectedDate: TextView
    private lateinit var btnAddEvent: Button
    private lateinit var recyclerView: RecyclerView
    private lateinit var adapter: EventAdapter
    
    // 数据库
    private lateinit var database: AppDatabase
    private lateinit var eventDao: EventDao
    private val eventsList = mutableListOf<Event>()
    private var selectedDateMillis: Long = System.currentTimeMillis()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        // 初始化数据库
        database = AppDatabase.getDatabase(this)
        eventDao = database.eventDao()
        
        // 初始化视图
        calendarView = findViewById(R.id.calendarView)
        tvSelectedDate = findViewById(R.id.tvSelectedDate)
        btnAddEvent = findViewById(R.id.btnAddEvent)
        recyclerView = findViewById(R.id.recyclerView)
        
        // 设置 RecyclerView
        adapter = EventAdapter(
            events = emptyList(),
            onItemClick = { event ->
                // 点击日程 - 显示详情
                showEventDetails(event)
            },
            onItemLongClick = { event ->
                // 长按日程 - 删除
                showDeleteConfirmDialog(event)
            }
        )
        recyclerView.layoutManager = LinearLayoutManager(this)
        recyclerView.adapter = adapter
        
        // 默认显示今天的日期
        showDate(System.currentTimeMillis())
        
        // 初始化列表
        updateEventsList()
        
        // 加载数据库中的日程
        loadAllEvents()
        
        // 日期选择监听
        calendarView.setOnDateChangeListener { view, year, month, dayOfMonth ->
            val calendar = Calendar.getInstance()
            calendar.set(year, month, dayOfMonth)
            selectedDateMillis = calendar.timeInMillis
            showDate(selectedDateMillis)
        }
        
        // 点击"添加日程"按钮
        btnAddEvent.setOnClickListener {
            showAddEventDialog()
        }
        
        Toast.makeText(this, "📅 日历已加载，数据会自动保存", Toast.LENGTH_SHORT).show()
    }
    
    private fun showDate(timeInMillis: Long) {
        val dateFormat = SimpleDateFormat("yyyy年MM月dd日 EEEE", Locale.CHINESE)
        val dateStr = dateFormat.format(Date(timeInMillis))
        tvSelectedDate.text = "选中日期：$dateStr"
    }
    
    // 弹出添加日程的对话框
    private fun showAddEventDialog() {
        // 加载自定义布局
        val dialogView = layoutInflater.inflate(R.layout.dialog_add_event, null)
        val etTitle = dialogView.findViewById<com.google.android.material.textfield.TextInputEditText>(R.id.etTitle)
        val etDesc = dialogView.findViewById<com.google.android.material.textfield.TextInputEditText>(R.id.etDescription)
        
        // 创建对话框
        AlertDialog.Builder(this)
            .setTitle("📝 添加日程")
            .setView(dialogView)
            .setPositiveButton("保存") { dialog, _ ->
                val title = etTitle?.text.toString().trim()
                val desc = etDesc?.text.toString().trim()
                
                if (title.isNotEmpty()) {
                    addEvent(title, desc)
                } else {
                    Toast.makeText(this, "标题不能为空", Toast.LENGTH_SHORT).show()
                }
            }
            .setNegativeButton("取消", null)
            .show()
    }
    
    // 从数据库加载所有日程
    private fun loadAllEvents() {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val events = eventDao.getAllEvents()
                withContext(Dispatchers.Main) {
                    eventsList.clear()
                    eventsList.addAll(events)
                    updateEventsList()
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@MainActivity, "加载失败: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
    
    // 添加日程
    private fun addEvent(title: String, description: String = "") {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val event = Event(
                    title = title,
                    description = description,
                    dateTime = selectedDateMillis
                )
                eventDao.insert(event)
                
                // 重新加载数据
                val events = eventDao.getAllEvents()
                withContext(Dispatchers.Main) {
                    eventsList.clear()
                    eventsList.addAll(events)
                    updateEventsList()
                    Toast.makeText(this@MainActivity, "✅ 添加成功！", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@MainActivity, "保存失败: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
    
    // 更新日程列表显示
    private fun updateEventsList() {
        adapter.updateEvents(eventsList)
    }
    
    // 显示日程详情
    private fun showEventDetails(event: Event) {
        val dateFormat = SimpleDateFormat("yyyy年MM月dd日 EEEE HH:mm", Locale.CHINESE)
        val dateStr = dateFormat.format(Date(event.dateTime))
        
        val message = buildString {
            append("📅 日期：$dateStr\n\n")
            append("📝 标题：${event.title}\n\n")
            if (event.description.isNotEmpty()) {
                append("💬 描述：${event.description}")
            }
        }
        
        AlertDialog.Builder(this)
            .setTitle("📋 日程详情")
            .setMessage(message)
            .setPositiveButton("确定", null)
            .setNegativeButton("删除") { _, _ ->
                deleteEvent(event)
            }
            .show()
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
    
    // 删除日程
    private fun deleteEvent(event: Event) {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                eventDao.delete(event)
                
                // 重新加载
                val events = eventDao.getAllEvents()
                withContext(Dispatchers.Main) {
                    eventsList.clear()
                    eventsList.addAll(events)
                    updateEventsList()
                    Toast.makeText(this@MainActivity, "🗑️ 删除成功！", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@MainActivity, "删除失败: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
}
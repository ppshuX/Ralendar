package com.ncu.kotlincalendar

import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * 日程实体类（对应数据库的表）
 */
@Entity(tableName = "events")
data class Event(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    
    val title: String,              // 标题
    val description: String = "",   // 描述
    val dateTime: Long,             // 日期时间（时间戳）
    val createdAt: Long = System.currentTimeMillis()  // 创建时间
)




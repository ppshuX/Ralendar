package com.ncu.kotlincalendar.data.models

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "events")
data class Event(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val title: String,
    val description: String = "",
    val dateTime: Long,
    val reminderMinutes: Int = 0,
    val subscriptionId: Long? = null,
    val locationName: String = "",
    val latitude: Double = 0.0,
    val longitude: Double = 0.0
)

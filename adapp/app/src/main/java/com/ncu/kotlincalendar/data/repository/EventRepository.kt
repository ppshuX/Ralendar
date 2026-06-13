package com.ncu.kotlincalendar.data.repository

import android.content.Context
import com.ncu.kotlincalendar.api.client.RetrofitClient
import com.ncu.kotlincalendar.data.database.AppDatabase
import com.ncu.kotlincalendar.data.database.EventDao
import com.ncu.kotlincalendar.data.models.Event
import com.ncu.kotlincalendar.utils.PreferenceManager
import java.text.SimpleDateFormat
import java.util.*

class EventRepository(private val context: Context) {

    private val eventDao: EventDao = AppDatabase.getDatabase(context).eventDao()
    private val api = RetrofitClient.api

    suspend fun getAllEvents(): Result<List<Event>> {
        return try {
            if (PreferenceManager.isCloudMode(context) && PreferenceManager.isLoggedIn(context)) {
                val token = PreferenceManager.getAccessToken(context) ?: return Result.failure(Exception("未登录"))
                val response = api.getEvents()
                if (response.isSuccessful) {
                    val cloudEvents = response.body()?.results ?: emptyList()
                    val events = cloudEvents.map { cloud ->
                        val dateFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
                        val dateTime = try {
                            dateFormat.parse(cloud.startTime)?.time ?: 0L
                        } catch (e: Exception) {
                            0L
                        }
                        Event(
                            id = cloud.id ?: 0,
                            title = cloud.title,
                            description = cloud.description,
                            dateTime = dateTime,
                            reminderMinutes = cloud.reminderMinutes,
                            locationName = cloud.location,
                            latitude = 0.0,
                            longitude = 0.0
                        )
                    }
                    Result.success(events)
                } else {
                    Result.failure(Exception("获取事件列表失败: ${response.message()}"))
                }
            } else {
                val events = eventDao.getUserEvents()
                Result.success(events)
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getEventsForDate(dateMillis: Long): Result<List<Event>> {
        return try {
            val calendar = java.util.Calendar.getInstance().apply {
                timeInMillis = dateMillis
                set(java.util.Calendar.HOUR_OF_DAY, 0)
                set(java.util.Calendar.MINUTE, 0)
                set(java.util.Calendar.SECOND, 0)
                set(java.util.Calendar.MILLISECOND, 0)
            }
            val startOfDay = calendar.timeInMillis
            calendar.add(java.util.Calendar.DAY_OF_MONTH, 1)
            val endOfDay = calendar.timeInMillis

            val events = eventDao.getEventsForDate(startOfDay, endOfDay)
            Result.success(events)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun createEvent(event: Event): Result<Event> {
        return try {
            if (PreferenceManager.isCloudMode(context) && PreferenceManager.isLoggedIn(context)) {
                val dateFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
                val cloudEvent = com.ncu.kotlincalendar.api.models.CloudEvent(
                    title = event.title,
                    description = event.description,
                    startTime = dateFormat.format(Date(event.dateTime)),
                    location = event.locationName,
                    reminderMinutes = event.reminderMinutes
                )
                val response = api.createEvent(cloudEvent)
                if (response.isSuccessful) {
                    val saved = response.body()
                    Result.success(event.copy(id = saved?.id ?: 0))
                } else {
                    Result.failure(Exception("创建事件失败: ${response.message()}"))
                }
            } else {
                val id = eventDao.insert(event)
                Result.success(event.copy(id = id))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun updateEvent(event: Event): Result<Unit> {
        return try {
            if (PreferenceManager.isCloudMode(context) && PreferenceManager.isLoggedIn(context)) {
                val dateFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
                val cloudEvent = com.ncu.kotlincalendar.api.models.CloudEvent(
                    id = event.id,
                    title = event.title,
                    description = event.description,
                    startTime = dateFormat.format(Date(event.dateTime)),
                    location = event.locationName,
                    reminderMinutes = event.reminderMinutes
                )
                val response = api.updateEvent(event.id, cloudEvent)
                if (response.isSuccessful) {
                    Result.success(Unit)
                } else {
                    Result.failure(Exception("更新事件失败: ${response.message()}"))
                }
            } else {
                eventDao.update(event)
                Result.success(Unit)
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun deleteEvent(event: Event): Result<Unit> {
        return try {
            if (PreferenceManager.isCloudMode(context) && PreferenceManager.isLoggedIn(context)) {
                val response = api.deleteEvent(event.id)
                if (response.isSuccessful) {
                    Result.success(Unit)
                } else {
                    Result.failure(Exception("删除事件失败: ${response.message()}"))
                }
            } else {
                eventDao.delete(event)
                Result.success(Unit)
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

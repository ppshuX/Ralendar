package com.ncu.kotlincalendar.data.managers

import android.util.Log
import com.ncu.kotlincalendar.api.services.ApiService
import com.ncu.kotlincalendar.data.database.EventDao
import com.ncu.kotlincalendar.data.database.SubscriptionDao
import com.ncu.kotlincalendar.data.models.Event
import com.ncu.kotlincalendar.data.models.Subscription
import java.time.Instant
import java.time.LocalDate
import java.time.ZoneId

class SubscriptionManager(
    private val subscriptionDao: SubscriptionDao,
    private val eventDao: EventDao,
    private val apiService: ApiService
) {

    companion object {
        private const val TAG = "SubscriptionManager"
    }

    suspend fun getAllSubscriptions(): List<Subscription> {
        return subscriptionDao.getAllSubscriptions()
    }

    suspend fun addSubscription(name: String, url: String = "", description: String = ""): Long {
        val subscription = Subscription(
            name = name,
            url = url,
            description = description,
            isEnabled = true
        )
        return subscriptionDao.insert(subscription)
    }

    suspend fun removeSubscription(id: Long) {
        subscriptionDao.deleteById(id)
    }

    suspend fun toggleSubscription(id: Long) {
        val subscription = subscriptionDao.getSubscriptionById(id) ?: return
        subscriptionDao.update(subscription.copy(isEnabled = !subscription.isEnabled))
    }

    suspend fun getVisibleEvents(dateMillis: Long? = null): List<Event> {
        val enabledSubscriptions = subscriptionDao.getEnabledSubscriptions()
        if (enabledSubscriptions.isEmpty()) return emptyList()

        val allEvents = mutableListOf<Event>()

        for (subscription in enabledSubscriptions) {
            try {
                val dbEvents = eventDao.getUserEvents().filter {
                    it.subscriptionId == subscription.id
                }
                allEvents.addAll(dbEvents)
            } catch (e: Exception) {
                Log.e(TAG, "获取订阅事件失败: ${subscription.name}", e)
            }
        }

        if (dateMillis != null) {
            val targetDate = Instant.ofEpochMilli(dateMillis)
                .atZone(ZoneId.systemDefault())
                .toLocalDate()
            return allEvents.filter { event ->
                val eventDate = Instant.ofEpochMilli(event.dateTime)
                    .atZone(ZoneId.systemDefault())
                    .toLocalDate()
                eventDate == targetDate
            }
        }

        return allEvents
    }

    suspend fun syncSubscription(subscription: Subscription) {
        try {
            val response = apiService.syncSubscription(subscription.id)
            if (response.isSuccessful) {
                Log.d(TAG, "订阅同步成功: ${subscription.name}")
            }
        } catch (e: Exception) {
            Log.e(TAG, "订阅同步失败: ${subscription.name}", e)
        }
    }
}

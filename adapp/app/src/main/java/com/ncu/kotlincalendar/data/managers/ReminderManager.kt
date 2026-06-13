package com.ncu.kotlincalendar.data.managers

import android.app.AlarmManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import android.util.Log
import com.ncu.kotlincalendar.data.models.Event
import com.ncu.kotlincalendar.utils.AlarmReceiver
import java.text.SimpleDateFormat
import java.util.*

class ReminderManager(private val context: Context) {

    private val alarmManager = context.getSystemService(Context.ALARM_SERVICE) as AlarmManager

    companion object {
        private const val TAG = "ReminderManager"
    }

    fun setReminder(event: Event) {
        if (event.reminderMinutes <= 0) return

        val reminderTime = event.dateTime - (event.reminderMinutes * 60 * 1000L)
        val currentTime = System.currentTimeMillis()

        if (reminderTime <= currentTime) {
            Log.d(TAG, "提醒时间已过，跳过设置: ${event.title}")
            return
        }

        val intent = Intent(context, AlarmReceiver::class.java).apply {
            putExtra("event_id", event.id)
            putExtra("event_title", event.title)
            putExtra("event_date_time", event.dateTime)
            putExtra("reminder_minutes", event.reminderMinutes)
        }

        val pendingIntent = PendingIntent.getBroadcast(
            context,
            event.id.toInt(),
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                if (alarmManager.canScheduleExactAlarms()) {
                    alarmManager.setExactAndAllowWhileIdle(
                        AlarmManager.RTC_WAKEUP,
                        reminderTime,
                        pendingIntent
                    )
                } else {
                    alarmManager.setAndAllowWhileIdle(
                        AlarmManager.RTC_WAKEUP,
                        reminderTime,
                        pendingIntent
                    )
                }
            } else {
                alarmManager.setExactAndAllowWhileIdle(
                    AlarmManager.RTC_WAKEUP,
                    reminderTime,
                    pendingIntent
                )
            }

            val df = SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.getDefault())
            Log.d(TAG, "提醒已设置: ${event.title} -> ${df.format(Date(reminderTime))}")
        } catch (e: Exception) {
            Log.e(TAG, "设置提醒失败", e)
        }
    }

    fun cancelReminder(eventId: Long) {
        val intent = Intent(context, AlarmReceiver::class.java)
        val pendingIntent = PendingIntent.getBroadcast(
            context,
            eventId.toInt(),
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        alarmManager.cancel(pendingIntent)
        Log.d(TAG, "提醒已取消: eventId=$eventId")
    }
}

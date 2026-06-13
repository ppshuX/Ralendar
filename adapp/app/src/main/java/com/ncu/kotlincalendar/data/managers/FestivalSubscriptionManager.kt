package com.ncu.kotlincalendar.data.managers

import android.content.Context
import android.content.SharedPreferences

class FestivalSubscriptionManager(context: Context) {

    private val sharedPreferences: SharedPreferences =
        context.getSharedPreferences("festival_prefs", Context.MODE_PRIVATE)

    companion object {
        private const val KEY_FIRST_INIT = "first_init_completed"
        private const val KEY_SUBSCRIBED_FESTIVALS = "subscribed_festivals"
    }

    fun isFirstInit(): Boolean {
        return !sharedPreferences.getBoolean(KEY_FIRST_INIT, false)
    }

    fun markFirstInitCompleted() {
        sharedPreferences.edit().putBoolean(KEY_FIRST_INIT, true).apply()
    }

    fun subscribeAll(festivalNames: List<String>) {
        val current = getSubscribedFestivals().toMutableSet()
        current.addAll(festivalNames)
        saveSubscribedFestivals(current)
    }

    fun subscribe(festivalName: String) {
        val current = getSubscribedFestivals().toMutableSet()
        current.add(festivalName)
        saveSubscribedFestivals(current)
    }

    fun unsubscribe(festivalName: String) {
        val current = getSubscribedFestivals().toMutableSet()
        current.remove(festivalName)
        saveSubscribedFestivals(current)
    }

    fun isSubscribed(festivalName: String): Boolean {
        return getSubscribedFestivals().any { subscribed ->
            subscribed == festivalName ||
            subscribed.contains(festivalName, ignoreCase = true) ||
            festivalName.contains(subscribed, ignoreCase = true) ||
            subscribed.split("/")[0].trim() == festivalName.split("/")[0].trim()
        }
    }

    fun getSubscribedFestivals(): Set<String> {
        val saved = sharedPreferences.getString(KEY_SUBSCRIBED_FESTIVALS, null)
        return if (saved.isNullOrEmpty()) {
            emptySet()
        } else {
            saved.split(",").filter { it.isNotEmpty() }.toSet()
        }
    }

    private fun saveSubscribedFestivals(festivals: Set<String>) {
        sharedPreferences.edit()
            .putString(KEY_SUBSCRIBED_FESTIVALS, festivals.joinToString(","))
            .apply()
    }
}

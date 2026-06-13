package com.ncu.kotlincalendar.data.database

import androidx.room.*
import com.ncu.kotlincalendar.data.models.Subscription

@Dao
interface SubscriptionDao {

    @Query("SELECT * FROM subscriptions ORDER BY createdAt DESC")
    suspend fun getAllSubscriptions(): List<Subscription>

    @Query("SELECT * FROM subscriptions WHERE isEnabled = 1")
    suspend fun getEnabledSubscriptions(): List<Subscription>

    @Query("SELECT * FROM subscriptions WHERE id = :id")
    suspend fun getSubscriptionById(id: Long): Subscription?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(subscription: Subscription): Long

    @Update
    suspend fun update(subscription: Subscription)

    @Delete
    suspend fun delete(subscription: Subscription)

    @Query("DELETE FROM subscriptions WHERE id = :id")
    suspend fun deleteById(id: Long)

    @Query("SELECT COUNT(*) FROM subscriptions")
    suspend fun getCount(): Int
}

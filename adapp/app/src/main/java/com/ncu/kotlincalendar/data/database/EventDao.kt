package com.ncu.kotlincalendar.data.database

import androidx.room.*
import com.ncu.kotlincalendar.data.models.Event

@Dao
interface EventDao {

    @Query("SELECT * FROM events ORDER BY dateTime ASC")
    suspend fun getAllEvents(): List<Event>

    @Query("SELECT * FROM events WHERE subscriptionId IS NULL ORDER BY dateTime ASC")
    suspend fun getUserEvents(): List<Event>

    @Query("SELECT * FROM events WHERE dateTime >= :startOfDay AND dateTime < :endOfDay")
    suspend fun getEventsForDate(startOfDay: Long, endOfDay: Long): List<Event>

    @Query("SELECT * FROM events WHERE dateTime >= :startOfDay AND dateTime < :endOfDay AND subscriptionId IS NULL")
    suspend fun getUserEventsForDate(startOfDay: Long, endOfDay: Long): List<Event>

    @Query("SELECT * FROM events WHERE id = :id")
    suspend fun getEventById(id: Long): Event?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(event: Event): Long

    @Update
    suspend fun update(event: Event)

    @Delete
    suspend fun delete(event: Event)

    @Query("DELETE FROM events WHERE id = :id")
    suspend fun deleteById(id: Long)

    @Query("SELECT * FROM events WHERE title LIKE '%' || :query || '%' OR description LIKE '%' || :query || '%'")
    suspend fun searchEvents(query: String): List<Event>
}

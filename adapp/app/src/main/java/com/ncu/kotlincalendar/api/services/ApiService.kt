package com.ncu.kotlincalendar.api.services

import com.ncu.kotlincalendar.api.models.*
import retrofit2.Response
import retrofit2.http.*

interface ApiService {

    @GET("api/weather/")
    suspend fun getWeather(@Query("city") city: String): WeatherResponse

    @GET("api/holiday/check/")
    suspend fun checkHoliday(@Query("date") date: String): HolidayResponse

    @GET("api/lunar/")
    suspend fun getLunarDate(@Query("date") date: String): LunarDateResponse

    @POST("api/ai/parse-event/")
    suspend fun parseEventFromText(@Body request: ParseEventRequest): ParseEventResponse

    @GET("api/events/")
    suspend fun getEvents(): Response<CloudEventListResponse>

    @POST("api/events/")
    suspend fun createEvent(@Body event: CloudEvent): Response<CloudEvent>

    @PUT("api/events/{id}/")
    suspend fun updateEvent(@Path("id") id: Long, @Body event: CloudEvent): Response<CloudEvent>

    @DELETE("api/events/{id}/")
    suspend fun deleteEvent(@Path("id") id: Long): Response<Unit>

    @GET("api/subscriptions/")
    suspend fun getSubscriptions(): Response<List<SubscriptionResponse>>

    @POST("api/subscriptions/{id}/sync/")
    suspend fun syncSubscription(@Path("id") id: Long): Response<SubscriptionResponse>
}

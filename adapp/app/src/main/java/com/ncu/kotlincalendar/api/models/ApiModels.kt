package com.ncu.kotlincalendar.api.models

import com.google.gson.annotations.SerializedName

data class WeatherResponse(
    @SerializedName("success")
    val success: Boolean,

    @SerializedName("data")
    val data: WeatherData? = null,

    @SerializedName("error")
    val error: String? = null
)

data class WeatherData(
    @SerializedName("location")
    val location: String,

    @SerializedName("weather")
    val weather: String,

    @SerializedName("temperature")
    val temperature: String,

    @SerializedName("feels_like")
    val feelsLike: String,

    @SerializedName("humidity")
    val humidity: String,

    @SerializedName("wind_dir")
    val windDir: String,

    @SerializedName("wind_scale")
    val windScale: String
)

data class HolidayResponse(
    @SerializedName("is_holiday")
    val isHoliday: Boolean,

    @SerializedName("lunar")
    val lunar: String? = null,

    @SerializedName("festivals")
    val festivals: List<FestivalInfo>? = null
)

data class FestivalInfo(
    @SerializedName("name")
    val name: String,

    @SerializedName("emoji")
    val emoji: String,

    @SerializedName("description")
    val description: String = ""
)

data class LunarDateResponse(
    @SerializedName("lunar_date")
    val lunarDate: String,

    @SerializedName("zodiac")
    val zodiac: String
)

data class SubscriptionResponse(
    @SerializedName("id")
    val id: Long,

    @SerializedName("name")
    val name: String,

    @SerializedName("events")
    val events: List<CloudEvent> = emptyList()
)

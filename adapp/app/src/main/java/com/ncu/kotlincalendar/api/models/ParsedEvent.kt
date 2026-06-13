package com.ncu.kotlincalendar.api.models

import com.google.gson.annotations.SerializedName

data class ParsedEvent(
    @SerializedName("title")
    val title: String,

    @SerializedName("date")
    val date: String,

    @SerializedName("time")
    val time: String? = null,

    @SerializedName("description")
    val description: String? = null
)

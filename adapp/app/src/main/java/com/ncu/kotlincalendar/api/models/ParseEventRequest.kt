package com.ncu.kotlincalendar.api.models

import com.google.gson.annotations.SerializedName

data class ParseEventRequest(
    @SerializedName("text")
    val text: String
)

data class ParseEventResponse(
    @SerializedName("success")
    val success: Boolean,

    @SerializedName("event")
    val event: ParsedEvent? = null,

    @SerializedName("error")
    val error: String? = null
)

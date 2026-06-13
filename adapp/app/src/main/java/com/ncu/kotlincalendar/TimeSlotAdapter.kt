package com.ncu.kotlincalendar

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.ncu.kotlincalendar.data.models.Event
import java.text.SimpleDateFormat
import java.util.*

class TimeSlotAdapter(
    private var events: List<Event>,
    private val onEventClick: (Event) -> Unit
) : RecyclerView.Adapter<TimeSlotAdapter.TimeSlotViewHolder>() {

    class TimeSlotViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val tvTime: TextView = view.findViewById(R.id.tvTimeSlot)
        val tvEventTitle: TextView = view.findViewById(R.id.tvTimeSlotEventTitle)
        val tvEventDesc: TextView = view.findViewById(R.id.tvTimeSlotEventDesc)
        val eventIndicator: View = view.findViewById(R.id.timeSlotEventIndicator)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): TimeSlotViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_time_slot, parent, false)
        return TimeSlotViewHolder(view)
    }

    override fun onBindViewHolder(holder: TimeSlotViewHolder, position: Int) {
        val event = events[position]
        val timeFormat = SimpleDateFormat("HH:mm", Locale.getDefault())

        holder.tvTime.text = timeFormat.format(Date(event.dateTime))
        holder.tvEventTitle.text = event.title

        if (event.description.isNotEmpty()) {
            holder.tvEventDesc.text = event.description
            holder.tvEventDesc.visibility = View.VISIBLE
        } else {
            holder.tvEventDesc.visibility = View.GONE
        }

        holder.eventIndicator.visibility = View.VISIBLE

        holder.itemView.setOnClickListener { onEventClick(event) }
    }

    override fun getItemCount(): Int = events.size

    fun updateEvents(newEvents: List<Event>) {
        events = newEvents.sortedBy { it.dateTime }
        notifyDataSetChanged()
    }
}

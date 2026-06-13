package com.ncu.kotlincalendar

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.ncu.kotlincalendar.data.models.Event
import java.text.SimpleDateFormat
import java.util.*

class EventAdapter(
    private var events: List<Event>,
    private val onItemClick: (Event) -> Unit,
    private val onItemLongClick: (Event) -> Unit
) : RecyclerView.Adapter<EventAdapter.EventViewHolder>() {

    class EventViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val tvTitle: TextView = view.findViewById(R.id.tvEventTitle)
        val tvTime: TextView = view.findViewById(R.id.tvEventTime)
        val tvDescription: TextView = view.findViewById(R.id.tvEventDescription)
        val tvLocation: TextView = view.findViewById(R.id.tvEventLocation)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): EventViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_event, parent, false)
        return EventViewHolder(view)
    }

    override fun onBindViewHolder(holder: EventViewHolder, position: Int) {
        val event = events[position]
        val timeFormat = SimpleDateFormat("HH:mm", Locale.getDefault())

        holder.tvTitle.text = event.title
        holder.tvTime.text = timeFormat.format(Date(event.dateTime))

        if (event.description.isNotEmpty()) {
            holder.tvDescription.text = event.description
            holder.tvDescription.visibility = View.VISIBLE
        } else {
            holder.tvDescription.visibility = View.GONE
        }

        if (event.locationName.isNotEmpty()) {
            holder.tvLocation.text = "📍 ${event.locationName}"
            holder.tvLocation.visibility = View.VISIBLE
        } else {
            holder.tvLocation.visibility = View.GONE
        }

        holder.itemView.setOnClickListener { onItemClick(event) }
        holder.itemView.setOnLongClickListener {
            onItemLongClick(event)
            true
        }
    }

    override fun getItemCount(): Int = events.size

    fun updateEvents(newEvents: List<Event>) {
        events = newEvents
        notifyDataSetChanged()
    }
}

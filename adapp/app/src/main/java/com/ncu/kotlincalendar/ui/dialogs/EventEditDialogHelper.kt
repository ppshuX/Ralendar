package com.ncu.kotlincalendar.ui.dialogs

import android.app.DatePickerDialog
import android.app.TimePickerDialog
import android.content.Context
import android.content.Intent
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.LinearLayout
import android.widget.Spinner
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import com.google.android.material.textfield.TextInputEditText
import com.ncu.kotlincalendar.MapPickerActivity
import com.ncu.kotlincalendar.R
import com.ncu.kotlincalendar.data.models.Event
import java.text.SimpleDateFormat
import java.time.LocalDate
import java.time.ZoneId
import java.util.*

class EventEditDialogHelper(
    private val context: Context,
    private val callback: OnEventSaveCallback
) {

    interface OnEventSaveCallback {
        fun onSave(
            event: Event?,
            title: String,
            description: String,
            dateTime: Long,
            reminderMinutes: Int,
            locationName: String,
            latitude: Double,
            longitude: Double
        )
    }

    private var selectedDateTime: Long = System.currentTimeMillis()
    private var selectedLocationName: String = ""
    private var selectedLatitude: Double = 0.0
    private var selectedLongitude: Double = 0.0
    private var currentDialog: AlertDialog? = null

    fun show(eventToEdit: Event? = null, defaultDate: LocalDate? = null) {
        val dialogView = android.view.LayoutInflater.from(context)
            .inflate(R.layout.dialog_event_edit, null)

        val etTitle = dialogView.findViewById<TextInputEditText>(R.id.etEventTitle)
        val etDescription = dialogView.findViewById<TextInputEditText>(R.id.etEventDescription)
        val etLocation = dialogView.findViewById<TextInputEditText>(R.id.etEventLocation)
        val tvDate = dialogView.findViewById<TextView>(R.id.tvSelectedDate)
        val tvTime = dialogView.findViewById<TextView>(R.id.tvSelectedTime)
        val btnSelectDate = dialogView.findViewById<Button>(R.id.btnSelectDate)
        val btnSelectTime = dialogView.findViewById<Button>(R.id.btnSelectTime)
        val btnSelectLocation = dialogView.findViewById<Button>(R.id.btnSelectLocation)
        val spinnerReminder = dialogView.findViewById<Spinner>(R.id.spinnerReminder)

        val dateFormat = SimpleDateFormat("yyyy年MM月dd日", Locale.CHINESE)
        val timeFormat = SimpleDateFormat("HH:mm", Locale.getDefault())

        if (eventToEdit != null) {
            etTitle.setText(eventToEdit.title)
            etDescription.setText(eventToEdit.description)
            selectedDateTime = eventToEdit.dateTime
            selectedLocationName = eventToEdit.locationName
            selectedLatitude = eventToEdit.latitude
            selectedLongitude = eventToEdit.longitude
        } else if (defaultDate != null) {
            selectedDateTime = defaultDate.atStartOfDay(ZoneId.systemDefault())
                .toInstant().toEpochMilli()
        }

        tvDate.text = dateFormat.format(Date(selectedDateTime))
        tvTime.text = timeFormat.format(Date(selectedDateTime))
        if (selectedLocationName.isNotEmpty()) {
            etLocation.setText(selectedLocationName)
        }

        val reminderOptions = arrayOf("不提醒", "提前5分钟", "提前15分钟", "提前30分钟", "提前1小时", "提前1天")
        val reminderValues = intArrayOf(0, 5, 15, 30, 60, 1440)
        val spinnerAdapter = ArrayAdapter(context, android.R.layout.simple_spinner_dropdown_item, reminderOptions)
        spinnerReminder.adapter = spinnerAdapter

        if (eventToEdit != null) {
            val index = reminderValues.indexOf(eventToEdit.reminderMinutes)
            if (index >= 0) spinnerReminder.setSelection(index)
        }

        btnSelectDate.setOnClickListener {
            val calendar = java.util.Calendar.getInstance().apply { timeInMillis = selectedDateTime }
            DatePickerDialog(context, { _, year, month, day ->
                val cal = java.util.Calendar.getInstance().apply {
                    set(year, month, day)
                    set(java.util.Calendar.HOUR_OF_DAY, java.util.Calendar.getInstance().get(java.util.Calendar.HOUR_OF_DAY))
                    set(java.util.Calendar.MINUTE, java.util.Calendar.getInstance().get(java.util.Calendar.MINUTE))
                    set(java.util.Calendar.SECOND, 0)
                    set(java.util.Calendar.MILLISECOND, 0)
                }
                selectedDateTime = cal.timeInMillis
                tvDate.text = dateFormat.format(Date(selectedDateTime))
            }, calendar.get(java.util.Calendar.YEAR), calendar.get(java.util.Calendar.MONTH), calendar.get(java.util.Calendar.DAY_OF_MONTH)).show()
        }

        btnSelectTime.setOnClickListener {
            val calendar = java.util.Calendar.getInstance().apply { timeInMillis = selectedDateTime }
            TimePickerDialog(context, { _, hour, minute ->
                val cal = java.util.Calendar.getInstance().apply { timeInMillis = selectedDateTime }
                cal.set(java.util.Calendar.HOUR_OF_DAY, hour)
                cal.set(java.util.Calendar.MINUTE, minute)
                selectedDateTime = cal.timeInMillis
                tvTime.text = timeFormat.format(Date(selectedDateTime))
            }, calendar.get(java.util.Calendar.HOUR_OF_DAY), calendar.get(java.util.Calendar.MINUTE), true).show()
        }

        btnSelectLocation.setOnClickListener {
            val intent = Intent(context, MapPickerActivity::class.java)
            (context as? android.app.Activity)?.startActivityForResult(intent, MapPickerActivity.REQUEST_CODE_MAP_PICKER)
        }

        val dialog = AlertDialog.Builder(context)
            .setView(dialogView)
            .setPositiveButton(if (eventToEdit != null) "更新" else "添加") { _, _ ->
                val title = etTitle.text.toString().trim()
                if (title.isEmpty()) {
                    Toast.makeText(context, "请输入日程标题", Toast.LENGTH_SHORT).show()
                    return@setPositiveButton
                }
                val description = etDescription.text.toString().trim()
                val locationName = etLocation.text.toString().trim()
                val reminderMinutes = reminderValues[spinnerReminder.selectedItemPosition]
                callback.onSave(
                    eventToEdit, title, description, selectedDateTime,
                    reminderMinutes, locationName, selectedLatitude, selectedLongitude
                )
            }
            .setNegativeButton("取消", null)
            .create()

        currentDialog = dialog
        dialog.show()
    }

    fun handleLocationResult(name: String, address: String, latitude: Double, longitude: Double) {
        selectedLocationName = if (address.isNotEmpty()) address else name
        selectedLatitude = latitude
        selectedLongitude = longitude
        currentDialog?.let { dialog ->
            val etLocation = dialog.findViewById<TextInputEditText>(R.id.etEventLocation)
            etLocation?.setText(selectedLocationName)
        }
    }
}

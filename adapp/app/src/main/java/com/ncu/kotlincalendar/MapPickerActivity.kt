package com.ncu.kotlincalendar

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.view.MenuItem
import android.widget.Button
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.google.android.material.textfield.TextInputEditText

class MapPickerActivity : AppCompatActivity() {

    companion object {
        const val REQUEST_CODE_MAP_PICKER = 2001
    }

    private lateinit var etSearch: TextInputEditText
    private lateinit var btnConfirm: Button
    private var selectedLatitude: Double = 0.0
    private var selectedLongitude: Double = 0.0
    private var selectedLocationName: String = ""

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_map_picker)

        supportActionBar?.apply {
            title = "选择地点"
            setDisplayHomeAsUpEnabled(true)
        }

        etSearch = findViewById(R.id.etSearchLocation)
        btnConfirm = findViewById(R.id.btnConfirmLocation)

        btnConfirm.setOnClickListener {
            val locationName = etSearch.text.toString().trim()
            if (locationName.isEmpty()) {
                Toast.makeText(this, "请输入地点名称", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            val resultIntent = Intent().apply {
                putExtra("location_name", locationName)
                putExtra("location_address", locationName)
                putExtra("latitude", selectedLatitude)
                putExtra("longitude", selectedLongitude)
            }
            setResult(Activity.RESULT_OK, resultIntent)
            finish()
        }
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        if (item.itemId == android.R.id.home) {
            finish()
            return true
        }
        return super.onOptionsItemSelected(item)
    }
}

package com.ncu.kotlincalendar

import android.os.Bundle
import android.view.MenuItem
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.ncu.kotlincalendar.api.client.RetrofitClient
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class FestivalDetailActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_festival_detail)

        supportActionBar?.apply {
            title = "节日详情"
            setDisplayHomeAsUpEnabled(true)
        }

        val festivalName = intent.getStringExtra("festival_name") ?: ""
        val festivalEmoji = intent.getStringExtra("festival_emoji") ?: ""
        val date = intent.getStringExtra("date") ?: ""

        val tvFestivalName = findViewById<TextView>(R.id.tvFestivalName)
        val tvFestivalEmoji = findViewById<TextView>(R.id.tvFestivalEmoji)
        val tvFestivalDate = findViewById<TextView>(R.id.tvFestivalDate)
        val tvFestivalDescription = findViewById<TextView>(R.id.tvFestivalDescription)

        tvFestivalEmoji.text = festivalEmoji
        tvFestivalName.text = festivalName
        tvFestivalDate.text = "日期：$date"

        loadFestivalDetail(festivalName, date, tvFestivalDescription)
    }

    private fun loadFestivalDetail(name: String, date: String, tvDescription: TextView) {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val response = RetrofitClient.api.checkHoliday(date)
                withContext(Dispatchers.Main) {
                    val festival = response.festivals?.find { it.name == name }
                    if (festival != null && festival.description.isNotEmpty()) {
                        tvDescription.text = festival.description
                    } else {
                        tvDescription.text = "暂无详细信息"
                    }
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    tvDescription.text = "加载失败，请稍后重试"
                }
            }
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

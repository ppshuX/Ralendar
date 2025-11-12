package com.ncu.kotlincalendar.ui.managers

import android.util.Log
import android.view.View
import android.widget.TextView
import androidx.lifecycle.LifecycleCoroutineScope
import com.google.android.material.card.MaterialCardView
import com.ncu.kotlincalendar.api.client.RetrofitClient
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

/**
 * 天气信息管理器
 * 
 * 职责：
 * - 加载实时天气数据
 * - 更新天气UI显示
 * - 处理天气加载失败
 * 
 * 使用方式：
 * ```kotlin
 * val weatherManager = WeatherManager(weatherCard, tvWeatherLocation, ...)
 * weatherManager.loadWeather(lifecycleScope)
 * ```
 */
class WeatherManager(
    private val weatherCard: MaterialCardView,
    private val tvWeatherLocation: TextView,
    private val tvTemperature: TextView,
    private val tvWeatherDesc: TextView,
    private val tvFeelsLike: TextView,
    private val tvHumidity: TextView,
    private val tvWind: TextView
) {
    
    /**
     * 加载天气信息
     * @param lifecycleScope Activity的生命周期协程作用域
     * @param location 城市名称，默认"北京"
     */
    fun loadWeather(
        lifecycleScope: LifecycleCoroutineScope,
        location: String = "北京"
    ) {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                // 调用后端API获取天气
                val response = RetrofitClient.api.getWeather(location)
                
                withContext(Dispatchers.Main) {
                    if (response.success && response.data != null) {
                        val weather = response.data
                        
                        // 更新UI
                        weatherCard.visibility = View.VISIBLE
                        tvWeatherLocation.text = weather.location
                        tvTemperature.text = "${weather.temperature}°"
                        tvWeatherDesc.text = weather.weather
                        tvFeelsLike.text = "体感 ${weather.feelsLike}°"
                        tvHumidity.text = "湿度 ${weather.humidity}%"
                        tvWind.text = "${weather.windDir} ${weather.windScale}级"
                        
                        Log.d(TAG, "天气加载成功: ${weather.location} ${weather.temperature}° ${weather.weather}")
                    } else {
                        // 加载失败，隐藏天气卡片
                        weatherCard.visibility = View.GONE
                        Log.e(TAG, "天气加载失败: ${response.error}")
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "获取天气失败", e)
                withContext(Dispatchers.Main) {
                    weatherCard.visibility = View.GONE
                }
            }
        }
    }
    
    companion object {
        private const val TAG = "WeatherManager"
    }
}


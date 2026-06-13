package com.ncu.kotlincalendar

import android.content.Intent
import android.os.Bundle
import android.view.MenuItem
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import com.ncu.kotlincalendar.utils.PreferenceManager

class SettingsActivity : AppCompatActivity() {

    private lateinit var tvLoginStatus: TextView
    private lateinit var tvCloudMode: TextView
    private lateinit var btnLogin: Button
    private lateinit var btnLogout: Button
    private lateinit var btnAbout: Button

    companion object {
        private const val REQUEST_LOGIN = 1001
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_settings)

        supportActionBar?.apply {
            title = "设置"
            setDisplayHomeAsUpEnabled(true)
        }

        tvLoginStatus = findViewById(R.id.tvLoginStatus)
        tvCloudMode = findViewById(R.id.tvCloudMode)
        btnLogin = findViewById(R.id.btnLogin)
        btnLogout = findViewById(R.id.btnLogout)
        btnAbout = findViewById(R.id.btnAbout)

        updateUI()

        btnLogin.setOnClickListener {
            val intent = Intent(this, LoginActivity::class.java)
            startActivityForResult(intent, REQUEST_LOGIN)
        }

        btnLogout.setOnClickListener {
            AlertDialog.Builder(this)
                .setTitle("退出登录")
                .setMessage("确定要退出登录吗？退出后将切换到本地模式。")
                .setPositiveButton("确定") { _, _ ->
                    PreferenceManager.logout(this)
                    updateUI()
                    Toast.makeText(this, "已退出登录", Toast.LENGTH_SHORT).show()
                }
                .setNegativeButton("取消", null)
                .show()
        }

        btnAbout.setOnClickListener {
            AlertDialog.Builder(this)
                .setTitle("关于 Ralendar")
                .setMessage("版本：1.0.0\n\nRalendar 是一款智能日历应用，提供日程管理、天气查询、节日订阅等功能。")
                .setPositiveButton("确定", null)
                .show()
        }
    }

    private fun updateUI() {
        val isLoggedIn = PreferenceManager.isLoggedIn(this)
        val isCloudMode = PreferenceManager.isCloudMode(this)

        if (isLoggedIn) {
            val userInfo = PreferenceManager.getUserInfo(this)
            tvLoginStatus.text = "已登录：${userInfo?.second ?: "未知用户"}"
            btnLogin.visibility = android.view.View.GONE
            btnLogout.visibility = android.view.View.VISIBLE
        } else {
            tvLoginStatus.text = "未登录"
            btnLogin.visibility = android.view.View.VISIBLE
            btnLogout.visibility = android.view.View.GONE
        }

        tvCloudMode.text = if (isCloudMode) "当前模式：☁️ 云端" else "当前模式：📱 本地"
    }

    @Deprecated("Deprecated in Java")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == REQUEST_LOGIN && resultCode == RESULT_OK) {
            updateUI()
            val loginSuccess = data?.getBooleanExtra("login_success", false) ?: false
            if (loginSuccess) {
                PreferenceManager.setCloudMode(this, true)
                Toast.makeText(this, "已自动切换到云端模式", Toast.LENGTH_SHORT).show()
            }
        }
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        if (item.itemId == android.R.id.home) {
            setResult(RESULT_OK)
            finish()
            return true
        }
        return super.onOptionsItemSelected(item)
    }
}

package com.ncu.kotlincalendar

import android.content.Intent
import android.os.Bundle
import android.view.MenuItem
import android.widget.Button
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.switchmaterial.SwitchMaterial
import com.ncu.kotlincalendar.data.database.AppDatabase
import com.ncu.kotlincalendar.data.database.SubscriptionDao
import com.ncu.kotlincalendar.data.models.Subscription
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class SubscriptionsActivity : AppCompatActivity() {

    private lateinit var recyclerView: RecyclerView
    private lateinit var btnAddSubscription: Button
    private lateinit var subscriptionDao: SubscriptionDao
    private var subscriptions = mutableListOf<Subscription>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_subscriptions)

        supportActionBar?.apply {
            title = "订阅管理"
            setDisplayHomeAsUpEnabled(true)
        }

        subscriptionDao = AppDatabase.getDatabase(this).subscriptionDao()
        recyclerView = findViewById(R.id.recyclerViewSubscriptions)
        btnAddSubscription = findViewById(R.id.btnAddSubscription)

        recyclerView.layoutManager = LinearLayoutManager(this)
        loadSubscriptions()

        btnAddSubscription.setOnClickListener {
            showAddSubscriptionDialog()
        }
    }

    private fun loadSubscriptions() {
        lifecycleScope.launch(Dispatchers.IO) {
            subscriptions = subscriptionDao.getAllSubscriptions().toMutableList()
            withContext(Dispatchers.Main) {
                val adapter = SubscriptionAdapter(
                    subscriptions,
                    onToggle = { subscription, enabled ->
                        lifecycleScope.launch(Dispatchers.IO) {
                            subscriptionDao.update(subscription.copy(isEnabled = enabled))
                        }
                    },
                    onDelete = { subscription ->
                        showDeleteConfirmDialog(subscription)
                    }
                )
                recyclerView.adapter = adapter
            }
        }
    }

    private fun showAddSubscriptionDialog() {
        val dialogView = layoutInflater.inflate(R.layout.dialog_add_subscription, null)
        val etName = dialogView.findViewById<com.google.android.material.textfield.TextInputEditText>(R.id.etSubscriptionName)
        val etUrl = dialogView.findViewById<com.google.android.material.textfield.TextInputEditText>(R.id.etSubscriptionUrl)

        AlertDialog.Builder(this)
            .setTitle("添加订阅")
            .setView(dialogView)
            .setPositiveButton("添加") { _, _ ->
                val name = etName.text.toString().trim()
                val url = etUrl.text.toString().trim()
                if (name.isNotEmpty()) {
                    lifecycleScope.launch(Dispatchers.IO) {
                        subscriptionDao.insert(Subscription(name = name, url = url))
                        withContext(Dispatchers.Main) {
                            Toast.makeText(this@SubscriptionsActivity, "订阅已添加", Toast.LENGTH_SHORT).show()
                            loadSubscriptions()
                        }
                    }
                } else {
                    Toast.makeText(this, "请输入订阅名称", Toast.LENGTH_SHORT).show()
                }
            }
            .setNegativeButton("取消", null)
            .show()
    }

    private fun showDeleteConfirmDialog(subscription: Subscription) {
        AlertDialog.Builder(this)
            .setTitle("删除订阅")
            .setMessage("确定要删除「${subscription.name}」吗？")
            .setPositiveButton("删除") { _, _ ->
                lifecycleScope.launch(Dispatchers.IO) {
                    subscriptionDao.delete(subscription)
                    withContext(Dispatchers.Main) {
                        Toast.makeText(this@SubscriptionsActivity, "已删除", Toast.LENGTH_SHORT).show()
                        loadSubscriptions()
                    }
                }
            }
            .setNegativeButton("取消", null)
            .show()
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        if (item.itemId == android.R.id.home) {
            finish()
            return true
        }
        return super.onOptionsItemSelected(item)
    }
}

class SubscriptionAdapter(
    private val subscriptions: List<Subscription>,
    private val onToggle: (Subscription, Boolean) -> Unit,
    private val onDelete: (Subscription) -> Unit
) : RecyclerView.Adapter<SubscriptionAdapter.SubscriptionViewHolder>() {

    class SubscriptionViewHolder(view: android.view.View) : RecyclerView.ViewHolder(view) {
        val tvName: android.widget.TextView = view.findViewById(R.id.tvSubscriptionName)
        val tvUrl: android.widget.TextView = view.findViewById(R.id.tvSubscriptionUrl)
        val switchEnabled: SwitchMaterial = view.findViewById(R.id.switchSubscriptionEnabled)
        val btnDelete: Button = view.findViewById(R.id.btnDeleteSubscription)
    }

    override fun onCreateViewHolder(parent: android.view.ViewGroup, viewType: Int): SubscriptionViewHolder {
        val view = android.view.LayoutInflater.from(parent.context)
            .inflate(R.layout.item_subscription, parent, false)
        return SubscriptionViewHolder(view)
    }

    override fun onBindViewHolder(holder: SubscriptionViewHolder, position: Int) {
        val subscription = subscriptions[position]
        holder.tvName.text = subscription.name
        holder.tvUrl.text = subscription.url
        holder.switchEnabled.isChecked = subscription.isEnabled

        holder.switchEnabled.setOnCheckedChangeListener { _, isChecked ->
            onToggle(subscription, isChecked)
        }

        holder.btnDelete.setOnClickListener {
            onDelete(subscription)
        }
    }

    override fun getItemCount(): Int = subscriptions.size
}

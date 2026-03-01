package com.sahayak.services

import android.accessibilityservice.AccessibilityService
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import android.util.Log
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.WebSocket
import okhttp3.WebSocketListener
import org.json.JSONObject

class AccessibilityMonitor : AccessibilityService() {

    private val TAG = "SahayakMonitor"
    private lateinit var webSocket: WebSocket
    private val client = OkHttpClient()

    override fun onServiceConnected() {
        super.onServiceConnected()
        Log.i(TAG, "Sahayak Accessibility Service Connected")
        initializeWebSocket()
    }

    private fun initializeWebSocket() {
        val request = Request.Builder().url("ws://localhost:8000/ws/scraper").build()
        webSocket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: okhttp3.Response) {
                Log.d(TAG, "WebSocket Connected to Local Python Backend")
            }
        })
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent) {
        val rootNode = rootInActiveWindow ?: return
        
        // Target packages: Uber, Zomato, Swiggy
        val packageName = event.packageName?.toString() ?: ""
        if (packageName.contains("uber") || packageName.contains("zomato") || packageName.contains("swiggy")) {
            scrapeOrderData(rootNode, packageName)
        }
    }

    private fun scrapeOrderData(node: AccessibilityNodeInfo, pkg: String) {
        val data = JSONObject()
        data.put("app", pkg)
        data.put("timestamp", System.currentTimeMillis())

        // Recursive scraping for relevant fields
        val textList = mutableListOf<String>()
        findTextNodes(node, textList)
        
        data.put("raw_ui_text", textList.joinToString(" | "))
        
        // Emit logic to local backend for RHR calculation
        if (textList.any { it.contains("₹") || it.contains("Rs") }) {
            webSocket.send(data.toString())
            Log.d(TAG, "Scraped Order Data Sent: ${data.toString()}")
        }
    }

    private fun findTextNodes(node: AccessibilityNodeInfo, list: MutableList<String>) {
        if (node.text != null) {
            list.add(node.text.toString())
        }
        for (i in 0 until node.childCount) {
            val child = node.getChild(i)
            if (child != null) {
                findTextNodes(child, list)
            }
        }
    }

    override fun onInterrupt() {}
}

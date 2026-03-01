package com.sahayak

import android.util.Log
import okhttp3.*
import org.json.JSONObject

object NativeBridge {
    private val client = OkHttpClient()
    private val request = Request.Builder().url("ws://localhost:8000/ws/market_data").build()
    private var webSocket: WebSocket? = null

    init {
        // Assume local companion orchestrator is running on 8000
        connectWebSocket()
    }

    private fun connectWebSocket() {
        webSocket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                Log.d("NativeBridge", "Sahayak Native Bridge Connected.")
            }
            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                Log.e("NativeBridge", "Websocket Connection Failed", t)
                // Implement offline caching retry logic here
            }
        })
    }

    fun sendDataToBackend(rawText: String) {
        val payload = JSONObject()
        payload.put("raw_screen_text", rawText)
        payload.put("source", "accessibility_service")
        
        webSocket?.send(payload.toString())
        Log.d("NativeBridge", "Propagated gig intelligence to Orchestrator.")
    }
}

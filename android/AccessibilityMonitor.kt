package com.sahayak

import android.accessibilityservice.AccessibilityService
import android.view.accessibility.AccessibilityEvent
import android.util.Log

class AccessibilityMonitor : AccessibilityService() {

    override fun onAccessibilityEvent(event: AccessibilityEvent) {
        if (event.eventType == AccessibilityEvent.TYPE_WINDOW_CONTENT_CHANGED ||
            event.eventType == AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED) {
            
            val source = event.source ?: return
            
            // Scraping logic for Uber/Zomato/Swiggy text nodes
            val textNodes = mutableListOf<String>()
            extractText(source, textNodes)
            
            val combinedText = textNodes.joinToString(" ")
            
            // Fast heuristic check for monetary or distance indicators
            if (combinedText.contains("₹") || combinedText.lowercase().contains("km")) {
                Log.d("Sahayak_Monitor", "Gig Ping Extracted: $combinedText")
                // Send raw data to Python backend via local WebSocket Bridge
                NativeBridge.sendDataToBackend(combinedText)
            }
        }
    }

    private fun extractText(node: android.view.accessibility.AccessibilityNodeInfo?, outList: MutableList<String>) {
        if (node == null) return
        if (node.text != null) {
            outList.add(node.text.toString())
        }
        for (i in 0 until node.childCount) {
            extractText(node.getChild(i), outList)
        }
    }

    override fun onInterrupt() {
        Log.w("Sahayak_Monitor", "Accessibility Service Interrupted")
    }
}

package com.example.data_collector

import android.content.Intent
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

var CHANNEL = "com.example/data_collector"

class MainActivity : FlutterActivity() {
    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        MethodChannel(
            flutterEngine.dartExecutor.binaryMessenger, CHANNEL
        )
            .setMethodCallHandler { call, result ->
                val args: HashMap<String, Any> = call.arguments as HashMap<String, Any>
                if (call.method == "StartService") {
                    val handle: Long = args["handle"] as Long;
                    Intent(this, BackgroundExecutorService::class.java)
                        .also { intent -> intent.putExtra("handle", handle) }
                        .also { intent ->
                            startService(intent)
                        }
                }
            }
    }
}

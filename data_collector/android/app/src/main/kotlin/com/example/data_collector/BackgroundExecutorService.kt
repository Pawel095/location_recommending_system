package com.example.data_collector

import android.app.*
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.os.*
import android.util.Log
import androidx.core.app.NotificationCompat
import io.flutter.FlutterInjector
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.embedding.engine.dart.DartExecutor
import io.flutter.plugin.common.MethodCall
import io.flutter.plugin.common.MethodChannel
import io.flutter.view.FlutterCallbackInformation
import java.lang.Exception


class BackgroundExecutorService : Service() {
    private val channelId = "data_collector Channel ID"
    private val stopSelfAction = "com.pawel095.data_collector.BackgroundExecutor.STOP_SELF"
    private val triggerDartAction =
        "com.pawel095.background_service.data_collector.TRIGGER_SCAN"

    private val notificationId = 1

    private val binder: IBinder = BackgroundExecutorBinder()
    private val broadcastReceiver = BackgroundExecutorBroadcastReceiver()

    private lateinit var flutterEngine: FlutterEngine
    private lateinit var methodChannel: MethodChannel

    lateinit var notifBuilder: NotificationCompat.Builder
    lateinit var notification: Notification


    inner class BackgroundExecutorBinder : Binder()

    inner class BackgroundExecutorBroadcastReceiver : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            when (intent?.action) {
                stopSelfAction -> {
                    Log.i("BackgroundExecutor", "StoppingService")
                    flutterEngine.serviceControlSurface.detachFromService()
                    flutterEngine.destroy()
                    stopSelf()
                }
            }
        }
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val serviceChannel = NotificationChannel(
                channelId, "BackgroundExecutor notification",
                NotificationManager.IMPORTANCE_DEFAULT
            )
            val manager = getSystemService(NotificationManager::class.java)
            manager!!.createNotificationChannel(serviceChannel)
        }
    }

    private fun registerBroadcastListener() {
        val intentFiler = IntentFilter()
        intentFiler.addAction(stopSelfAction)
        intentFiler.addAction(triggerDartAction)
        intentFiler.addCategory(Intent.CATEGORY_DEFAULT)
        registerReceiver(broadcastReceiver, intentFiler)
    }

    private fun executeHandle(handle: Long) {
        val callback = FlutterCallbackInformation.lookupCallbackInformation(handle)
        if (callback == null) {
            Log.e("BackgroundExecutor", "callback handle not found")
            throw Exception("Bad callback")
        }
        val dartCodeHandle = DartExecutor.DartCallback(
            assets,
            FlutterInjector.instance().flutterLoader().findAppBundlePath(),
            callback
        )
        flutterEngine.dartExecutor.executeDartCallback(dartCodeHandle)
    }

    private fun createFlutterEngine() {
        if (!FlutterInjector.instance().flutterLoader().initialized()) {
            FlutterInjector.instance().flutterLoader().startInitialization(applicationContext)
        }
        FlutterInjector.instance().flutterLoader()
            .ensureInitializationComplete(applicationContext, null)


        val flutterEngine = FlutterEngine(this@BackgroundExecutorService)
        flutterEngine.serviceControlSurface.attachToService(
            this@BackgroundExecutorService,
            null,
            true
        )
        this.flutterEngine = flutterEngine
    }

    override fun onBind(intent: Intent): IBinder {
        return this.binder
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        super.onStartCommand(intent, flags, startId)
        notifBuilder = NotificationCompat.Builder(this, channelId)
        val handle: Long? = intent?.getLongExtra("handle", 0)
        if (handle == null || handle == 0L) {
            throw Exception("handle is null ==> Die.")
        }

        registerBroadcastListener()
        createNotificationChannel()
        createFlutterEngine()
        this.methodChannel = MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL)
        methodChannel.setMethodCallHandler { call, result -> methodChannelExecutor(call, result) }
        executeHandle(handle)

        val stopIntent = Intent()
        stopIntent.action = stopSelfAction
        stopIntent.addCategory(Intent.CATEGORY_DEFAULT)
        val pStopSelf =
            PendingIntent.getBroadcast(this, 0, stopIntent, PendingIntent.FLAG_IMMUTABLE)

        updateNotification {
            it.setContentTitle("Location is collected")
                .setOnlyAlertOnce(true)
                .setSmallIcon(R.drawable.ic_launcher_foreground)
                .addAction(R.drawable.ic_launcher_foreground, "Stop", pStopSelf)
                .setPriority(NotificationManager.IMPORTANCE_LOW)
        }
        startForeground(notificationId, notification)
        runService()
        return START_REDELIVER_INTENT
    }

    private fun updateNotification(builder: (n: NotificationCompat.Builder) -> NotificationCompat.Builder) {
        notification = builder(notifBuilder).build()
    }

    private fun methodChannelExecutor(call: MethodCall, result: MethodChannel.Result) {
        val args: HashMap<String, Any> = call.arguments as HashMap<String, Any>
        when (call.method) {
            "UPDATE_NOTIFICATION" -> {
                val errors = args["errors"]
                val qSize = args["qSize"]
                val lastcode = args["lastcode"]
                val nextUpdate = args["nextUpdate"]
                updateNotification { it.setContentText("Err: $errors, Q.len: $qSize, code: $lastcode, nex: $nextUpdate") }
                    .let { getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager }
                    .also { it.notify(notificationId, notification) }
            }
        }
    }


    private fun runService() = Intent().also { intent ->
        intent.action = triggerDartAction
        intent.addCategory(Intent.CATEGORY_DEFAULT)
    }.let { intent ->
        PendingIntent.getBroadcast(this@BackgroundExecutorService, 0, intent, 0)
    }.send()


    override fun onDestroy() {
        super.onDestroy()
        unregisterReceiver(broadcastReceiver)
    }

    override fun onCreate() {
        super.onCreate()
        Log.d("BackgroundExecutor", "onCreate called")
    }

}
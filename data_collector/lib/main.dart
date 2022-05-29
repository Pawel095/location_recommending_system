import 'dart:async';
import 'dart:collection';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_logs/flutter_logs.dart';
import 'package:geolocator/geolocator.dart';
import 'package:http/http.dart' as http;

import 'package:data_collector/environment.dart';
import 'package:data_collector/router/Router.dart';
import 'package:data_collector/util/PlatformComms.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  PlatformComms().configure(serviceContext);
  runApp(MyApp(
    appRouter: AppRouter(),
  ));
}

Future<void> serviceContext() async {
  final Queue<Position> toUpload = Queue();
  const platform = MethodChannel('com.example/data_collector');
  final uploadEndpoint = Uri.parse(Environment.SCANPOINT_URL);
  const uploadTimer = Duration(seconds: 5);
  var errors = 0;
  var lastcode = 0;

  int makedatime(DateTime nextUpload) {
    return nextUpload.millisecondsSinceEpoch;
    // return "${nextUpload.hour}:${nextUpload.minute}:${nextUpload.second}";
  }

  var nu = makedatime(DateTime.now());

  Timer.periodic(const Duration(seconds: 10), (timer) async {
    Position p = await Geolocator.getCurrentPosition(
      timeLimit: const Duration(seconds: 7),
    );
    toUpload.add(p);
  });

  Timer.periodic(const Duration(seconds: 1), (timer) async {
    // Notification update
    platform.invokeMethod("UPDATE_NOTIFICATION", {
      "errors": errors,
      "qSize": toUpload.length,
      "lastcode": lastcode,
      "nextUpdate": nu
    });
  });

  Timer.periodic(uploadTimer, (timer) async {
    nu = makedatime(DateTime.now().add(uploadTimer));
    if (toUpload.length < 30) {
      // FlutterLogs.logInfo("SERVICE", "UPLOADER",
      // "Not enough items in queue: ${toUpload.length}");
      return;
    }
    var client = http.Client();

    List<Position> points = [];
    for (var i = 0; i < 50; i++) {
      if (toUpload.isEmpty) break;
      points.add(toUpload.removeFirst());
    }
    // FlutterLogs.logInfo(
    // "SERIVCE", "UPLOAD", "Preparing to upload ${points.length} points");
    try {
      List<Map<String, String>> mapped = points
          .map((e) => {
                "latitude": e.latitude.toString(),
                "longitude": e.longitude.toString(),
                "timestamp": e.timestamp.toString(),
                "accuracy": e.accuracy.toString(),
                "altitude": e.altitude.toString()
              })
          .toList();
      var response = await client.post(
        uploadEndpoint,
        body: jsonEncode(mapped),
        headers: {
          'Content-Type': 'application/json; charset=UTF-8',
        },
      );
      lastcode = response.statusCode;
      if (response.statusCode != 200) {
        // FlutterLogs.logError("SERIVCE", "UPLOAD",
        // "API error ${response.statusCode}: ${response.body}");
        errors += 1;
      }
      // FlutterLogs.logInfo("SERIVCE", "UPLOAD", "Success: $mapped");
    } catch (e) {
      // The request died, return the elements to the queue in the same order.
      toUpload.addAll(points.reversed);
      // FlutterLogs.logWarn("SERIVCE", "UPLOAD", "Error: $e");
      errors += 1;
    } finally {
      client.close();
    }
  });

  WidgetsFlutterBinding.ensureInitialized();
  await FlutterLogs.initLogs(
    logLevelsEnabled: [
      LogLevel.INFO,
      LogLevel.WARNING,
      LogLevel.ERROR,
      LogLevel.SEVERE
    ],
    timeStampFormat: TimeStampFormat.TIME_FORMAT_READABLE,
    directoryStructure: DirectoryStructure.SINGLE_FILE_FOR_DAY,
    logTypesEnabled: ["device", "network", "errors", "SERVICE"],
    logFileExtension: LogFileExtension.LOG,
    logsWriteDirectoryName: "MyLogs",
    logsExportDirectoryName: "MyLogs/Exported",
    debugFileOperations: true,
    isDebuggable: true,
    autoClearLogs: false,
  );

  // platform.setMethodCallHandler((call) async {
  //   switch (call.method) {
  //     case "1":
  //       getGPSPoint();
  //       return;
  //     default:
  //   }
  // });
  print("dart-service initialized");
}

class MyApp extends StatelessWidget {
  final AppRouter appRouter;
  const MyApp({
    Key? key,
    required this.appRouter,
  });

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Gps 2 Api',
      onGenerateRoute: appRouter.onGenerateRouter,
    );
  }
}

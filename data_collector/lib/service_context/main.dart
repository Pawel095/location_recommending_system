import 'dart:async';
import 'dart:collection';
import 'dart:convert';

import 'package:data_collector/service_context/util.dart';
import 'package:flutter/services.dart';
import 'package:geolocator/geolocator.dart';
import 'package:http/http.dart' as http;

import 'package:data_collector/environment.dart';

Future<void> serviceContext() async {
  final Queue<Position> toUpload = Queue();
  const platform = MethodChannel('com.example/data_collector');
  final uploadEndpoint = Uri.parse(Environment.DATA_COLLECTION_UPLOAD_ENDPOINT);
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
      return;
    }
    var client = http.Client();

    List<Position> points = [];
    for (var i = 0; i < 50; i++) {
      if (toUpload.isEmpty) break;
      points.add(toUpload.removeFirst());
    }
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
        errors += 1;
      }
    } catch (e) {
      // The request died, return the elements to the queue in the same order.
      toUpload.addAll(points.reversed);
      errors += 1;
    } finally {
      client.close();
    }
  });
  initailizeLogger();
  if (Environment.DEBUG) {
    print("dart-service initialized");
  }
}

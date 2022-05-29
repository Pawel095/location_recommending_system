import 'dart:ui';

import 'package:flutter/services.dart';

class PlatformComms {
  final platform = const MethodChannel("com.example/data_collector");

  late int bgExecHandle;

  static final PlatformComms _self = PlatformComms._internal();

  PlatformComms._internal();
  factory PlatformComms() {
    return _self;
  }

  void configure(Function serviceContext) {
    CallbackHandle? handle = PluginUtilities.getCallbackHandle(serviceContext);
    if (handle == null) {
      throw Exception("The callback is not accesible ==> Die.");
    }
    bgExecHandle = handle.toRawHandle();
  }

  void startService() {
    platform.invokeMethod("StartService", {"handle": bgExecHandle});
  }
}

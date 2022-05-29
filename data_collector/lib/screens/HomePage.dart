// ignore_for_file: use_build_context_synchronously

import 'dart:io';

import 'package:data_collector/cubit/apistatus_cubit.dart';
import 'package:data_collector/environment.dart';
import 'package:data_collector/util/PlatformComms.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_logs/flutter_logs.dart';
import 'package:geolocator/geolocator.dart';
import 'package:http/http.dart' as http;

class HomePage extends StatefulWidget {
  HomePage({Key? key, required this.title}) : super(key: key);

  final String title;

  @override
  _HomePageState createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  Future<void> askForLocationPermissions() async {
    bool serviceEnabled;
    LocationPermission permission;
    serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      return Future.error('Location services are disabled.');
    }
    permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        return Future.error('Location permissions are denied');
      }
    }

    if (permission == LocationPermission.deniedForever) {
      return Future.error(
          'Location permissions are permanently denied, we cannot request permissions.');
    }
    await Geolocator.openLocationSettings();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
      ),
      body: BlocProvider(
        create: (context) => ApistatusCubit(),
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: <Widget>[
              TextButton(
                onPressed: () {
                  PlatformComms().startService();
                },
                child: Text("Start Service"),
              ),
              TextButton(
                onPressed: () => askForLocationPermissions(),
                child: Text("Request Location Permission"),
              ),
              TextButton(
                onPressed: () =>
                    FlutterLogs.exportLogs(exportType: ExportType.ALL),
                child: Text("Export logs"),
              ),
              Builder(
                builder: (context) => TextButton(
                  onPressed: () async {
                    context.read<ApistatusCubit>().updateText("Checking...");
                    try {
                      var ret =
                          await http.get(Uri.parse(Environment.BACKEND_URL));
                      context
                          .read<ApistatusCubit>()
                          .updateText("${ret.statusCode}:${ret.body}");
                    } on SocketException catch (e) {
                      context.read<ApistatusCubit>().updateText(e.message);
                    }
                  },
                  child: Text("Api Status"),
                ),
              ),
              BlocBuilder<ApistatusCubit, ApistatusState>(
                builder: (context, state) {
                  return Text(state.status);
                },
              )
            ],
          ),
        ),
      ),
    );
  }
}

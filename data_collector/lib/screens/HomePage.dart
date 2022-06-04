// ignore_for_file: file_names

import 'package:data_collector/cubit/apistatus_cubit.dart';
import 'package:data_collector/environment.dart';
import 'package:data_collector/router/AppRouter.dart';
import 'package:data_collector/util/PlatformComms.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:geolocator/geolocator.dart';

class HomePage extends StatelessWidget {
  const HomePage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        actions: buildActions(),
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
                child: const Text("Start Service"),
              ),
              TextButton(
                onPressed: () => askForLocationPermissions(),
                child: const Text("Request Location Permission"),
              )
            ],
          ),
        ),
      ),
    );
  }

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

  List<Widget> buildActions() {
    List<Widget> actions = [];

    if (Environment.DEBUG) {
      actions.add(
        Builder(
          builder: (context) => IconButton(
            icon: const Icon(Icons.warning),
            onPressed: () =>
                {Navigator.pushNamed(context, AppRouter.DEBUG_PAGE)},
          ),
        ),
      );
    }
    return actions;
  }
}

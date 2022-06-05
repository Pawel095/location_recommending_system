import 'dart:convert';

import 'package:data_collector/environment.dart';
import 'package:data_collector/util/PositionToWKT.dart';
import 'package:flutter/material.dart';
import 'package:flutter_osm_plugin/flutter_osm_plugin.dart';
import 'package:geolocator/geolocator.dart';
import 'package:http/http.dart' as http;

class RecomendationPage extends StatefulWidget {
  const RecomendationPage({Key? key}) : super(key: key);

  @override
  State<RecomendationPage> createState() => _RecomendationPageState();
}

class _RecomendationPageState extends State<RecomendationPage> {
  late MapController controller;
  final GeoPoint initpos =
      GeoPoint(latitude: 51.7514502, longitude: 19.4459872);
  _RecomendationPageState() {
    controller = MapController(initPosition: initpos);
  }

  void loadingDialog(BuildContext context) async {
    showDialog(
        context: context,
        barrierDismissible: false,
        builder: (_) {
          return SimpleDialog(children: [
            Center(
              child: Column(
                children: const [
                  CircularProgressIndicator(),
                  Text("Requesting location recommendations")
                ],
              ),
            ),
          ]);
        });
    dynamic navigator = Navigator.of(context);
    // do shit here
    Position p = await Geolocator.getCurrentPosition(
      timeLimit: const Duration(seconds: 7),
    );
    String wkt = positionToWKT(p);
    dynamic result = await http.post(
      Uri.parse("${Environment.RECOMENDATION_ENDPOINT_URL}/0"),
      body: jsonEncode({"wkt": wkt}),
      headers: {"Content-Type": "application/json"},
    );
    var xy = [0.0, 0.0];
    var bodyParsed = jsonDecode(result.body);
    for (var point in bodyParsed) {
      xy[0] += point["x"];
      xy[1] += point["y"];
      await controller
          .addMarker(GeoPoint(latitude: point["x"], longitude: point["y"]));
    }
    xy[0] /= bodyParsed.length;
    xy[1] /= bodyParsed.length;
    await controller.goToLocation(GeoPoint(latitude: xy[0], longitude: xy[1]));
    await controller.setZoom(zoomLevel: 11);
    navigator.pop();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Recomendation View")),
      body: OSMFlutter(
        controller: controller,
        initZoom: 19,
        markerOption: MarkerOption(
          defaultMarker: const MarkerIcon(
            icon: Icon(
              Icons.person_pin_circle,
              color: Colors.blue,
              size: 56,
            ),
          ),
        ),
      ),
      floatingActionButton: Builder(builder: (context) {
        return FloatingActionButton(
          child: const Text("Recommend"),
          onPressed: () async {
            loadingDialog(context);
          },
        );
      }),
    );
  }
}

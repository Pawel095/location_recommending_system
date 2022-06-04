import 'package:flutter/material.dart';
import 'package:flutter_osm_plugin/flutter_osm_plugin.dart';

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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Recomendation View")),
      body: Container(
        child: OSMFlutter(
          controller: controller,
          initZoom: 19,
          markerOption: MarkerOption(
              defaultMarker: const MarkerIcon(
            icon: Icon(
              Icons.person_pin_circle,
              color: Colors.blue,
              size: 56,
            ),
          )),
        ),
      ),
      floatingActionButton: FloatingActionButton(
        child: const Text("Recommend"),
        onPressed: () async {
          await controller
              .changeLocation(GeoPoint(latitude: 51.7514, longitude: 19.44791));
          dynamic a = 1;
        },
      ),
    );
  }
}

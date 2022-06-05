import 'package:geolocator/geolocator.dart';

String positionToWKT(Position p) {
  return "POINT (${p.latitude} ${p.longitude})";
}

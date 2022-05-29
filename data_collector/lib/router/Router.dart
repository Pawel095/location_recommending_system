import 'package:data_collector/screens/Error.dart';
import 'package:data_collector/screens/HomePage.dart';
import 'package:flutter/material.dart';

class AppRouter {
  Route onGenerateRouter(RouteSettings rs) {
    switch (rs.name) {
      case '/':
        return MaterialPageRoute(builder: (_) => HomePage(title: "Home"));
      default:
        return MaterialPageRoute(builder: (_) => ErrorScreen());
    }
  }
}

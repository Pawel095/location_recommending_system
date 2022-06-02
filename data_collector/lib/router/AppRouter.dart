// ignore_for_file: constant_identifier_names

import 'package:data_collector/screens/Error.dart';
import 'package:data_collector/screens/RecommendationPage.dart';
import 'package:flutter/material.dart';

import '../screens/DebugPage.dart';
import '../screens/HomePage.dart';

class AppRouter {
  static const DEFAULT = '/';
  static const RECOMENDATION_PAGE = '/UserPage';
  static const DEBUG_PAGE = '/DebugMenu';
  Route onGenerateRouter(RouteSettings rs) {
    switch (rs.name) {
      case DEFAULT:
        return MaterialPageRoute(builder: (_) => const HomePage());
      case RECOMENDATION_PAGE:
        return MaterialPageRoute(builder: (_) => const RecomendationPage());
      case DEBUG_PAGE:
        return MaterialPageRoute(
            builder: (_) => const DebugPage(title: "Debug Menu"));
      default:
        return MaterialPageRoute(builder: (_) => const ErrorScreen());
    }
  }
}

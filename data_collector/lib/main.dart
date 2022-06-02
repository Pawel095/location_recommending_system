import 'package:data_collector/environment.dart';
import 'package:data_collector/router/AppRouter.dart';
import 'package:data_collector/service_context/main.dart';
import 'package:data_collector/util/PlatformComms.dart';
import 'package:flutter/material.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  PlatformComms().configure(serviceContext);
  runApp(MyApp(
    appRouter: AppRouter(),
  ));
}

class MyApp extends StatelessWidget {
  final AppRouter appRouter;
  const MyApp({
    Key? key,
    required this.appRouter,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Data Collection App',
      onGenerateRoute: appRouter.onGenerateRouter,
      initialRoute: Environment.initialRoute,
    );
  }
}

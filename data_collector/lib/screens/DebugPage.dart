// ignore_for_file: use_build_context_synchronously

import 'dart:io';

import 'package:data_collector/cubit/apistatus_cubit.dart';
import 'package:data_collector/environment.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_logs/flutter_logs.dart';
import 'package:http/http.dart' as http;

class DebugPage extends StatefulWidget {
  const DebugPage({Key? key, required this.title}) : super(key: key);

  final String title;

  @override
  DebugPageState createState() => DebugPageState();
}

class DebugPageState extends State<DebugPage> {
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
                onPressed: () =>
                    FlutterLogs.exportLogs(exportType: ExportType.ALL),
                child: const Text("Export logs"),
              ),
              checkAPIStatusButton(),
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

  Builder checkAPIStatusButton() {
    return Builder(
      builder: (context) => TextButton(
        onPressed: () async {
          context.read<ApistatusCubit>().updateText("Checking...");
          try {
            var ret =
                await http.get(Uri.parse(Environment.DATA_COLLECTION_API_URL));
            context
                .read<ApistatusCubit>()
                .updateText("${ret.statusCode}:${ret.body}");
          } on SocketException catch (e) {
            context.read<ApistatusCubit>().updateText(e.message);
          }
        },
        child: const Text("Api Status"),
      ),
    );
  }
}

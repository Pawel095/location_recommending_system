import 'package:flutter/material.dart';

class ErrorScreen extends StatelessWidget {
  const ErrorScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("ERROR!"),
      ),
      body: Center(
        child: Column(
          children: [
            Text("Error!\n The developer made a mistake in the router!")
          ],
        ),
      ),
    );
  }
}

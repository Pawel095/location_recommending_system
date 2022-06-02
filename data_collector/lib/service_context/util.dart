import 'package:flutter/cupertino.dart';
import 'package:flutter_logs/flutter_logs.dart';

Future<void> initailizeLogger() async {
  WidgetsFlutterBinding.ensureInitialized();
  await FlutterLogs.initLogs(
    logLevelsEnabled: [
      LogLevel.INFO,
      LogLevel.WARNING,
      LogLevel.ERROR,
      LogLevel.SEVERE
    ],
    timeStampFormat: TimeStampFormat.TIME_FORMAT_READABLE,
    directoryStructure: DirectoryStructure.SINGLE_FILE_FOR_DAY,
    logTypesEnabled: ["device", "network", "errors", "SERVICE"],
    logFileExtension: LogFileExtension.LOG,
    logsWriteDirectoryName: "MyLogs",
    logsExportDirectoryName: "MyLogs/Exported",
    debugFileOperations: true,
    isDebuggable: true,
    autoClearLogs: false,
  );
}

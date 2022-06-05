class Environment {
  static const bool DEBUG = true;

  static const String DATA_COLLECTION_API_URL = "http://192.168.2.7:8000";

  static const String DATA_COLLECTION_UPLOAD_ENDPOINT =
      "$DATA_COLLECTION_API_URL/scanpoint";

  static const String RECOMENDATION_API_URL = "http://192.168.2.7:8888";

  static const String RECOMENDATION_ENDPOINT_URL =
      "$RECOMENDATION_API_URL/recomend";

  static const String initialRoute = "/";
}

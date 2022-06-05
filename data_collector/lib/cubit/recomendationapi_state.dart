part of 'recomendationapi_cubit.dart';

class RecomendationapiState extends Equatable {
  final String lastResponse;
  const RecomendationapiState({
    required this.lastResponse,
  });
  @override
  List<Object> get props => [];
}

class RecomendationapiInitial extends RecomendationapiState {
  const RecomendationapiInitial({required super.lastResponse});
}

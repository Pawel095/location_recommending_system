import 'package:bloc/bloc.dart';
import 'package:equatable/equatable.dart';

part 'recomendationapi_state.dart';

class RecomendationapiCubit extends Cubit<RecomendationapiState> {
  RecomendationapiCubit()
      : super(const RecomendationapiInitial(lastResponse: ''));
  update(String text) => emit(RecomendationapiState(lastResponse: text));
}

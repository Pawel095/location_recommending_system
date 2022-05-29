import 'package:bloc/bloc.dart';
import 'package:equatable/equatable.dart';

part 'apistatus_state.dart';

class ApistatusCubit extends Cubit<ApistatusState> {
  ApistatusCubit() : super(ApistatusInitial());
  updateText(String text) => emit(ApistatusState(status: text));
}

part of 'apistatus_cubit.dart';

class ApistatusState extends Equatable {
  const ApistatusState({this.status = ""});
  final String status;

  @override
  List<Object> get props => [status];
}

class ApistatusInitial extends ApistatusState {}

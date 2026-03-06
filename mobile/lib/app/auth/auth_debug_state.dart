import 'package:flutter/foundation.dart';

class AuthDebugState extends ChangeNotifier {
  AuthDebugState._();

  static final AuthDebugState instance = AuthDebugState._();

  bool firebaseInitDone = false;
  String? lastCode;
  String? lastMessage;

  void setFirebaseInitDone(bool value) {
    firebaseInitDone = value;
    notifyListeners();
  }

  void setAuthError({String? code, String? message}) {
    lastCode = code;
    lastMessage = message;
    notifyListeners();
  }

  void clearAuthError() {
    lastCode = null;
    lastMessage = null;
    notifyListeners();
  }
}

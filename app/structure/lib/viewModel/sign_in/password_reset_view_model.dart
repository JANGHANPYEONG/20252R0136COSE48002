import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:structure/config/palette.dart';
import 'package:structure/model/user_model.dart';

class PasswordResetViewModel with ChangeNotifier {
  UserModel userModel;
  BuildContext context;
  PasswordResetViewModel({required this.userModel, required this.context});

  final formKey = GlobalKey<FormState>();
  bool isLoading = false;
  bool isActivateButton = false;
  bool _isValidEmail = false;

  TextEditingController email = TextEditingController();

  // 이메일이 입력됐는지 확인
  String? emailValidate(String? value) {
    notifyListeners();
    if (value!.isEmpty) {
      _isValidEmail = false;
      return '이메일을 입력하세요';
    } else {
      _isValidEmail = true;
      return null;
    }
  }

  /// 값이 올바르게 입력됐는지 확인
  bool isValid() {
    if (_isValidEmail) {
      return true;
    } else {
      return false;
    }
  }

  /// 비밀번호 변경
  Future<void> sendResetPassword() async {
    isLoading = true;
    notifyListeners();

    try {
      await FirebaseAuth.instance.sendPasswordResetEmail(email: email.text);

      _success();
    } on FirebaseException catch (e) {
      if (e.code == 'invalid-email') {
        _showAlert('잘못된 이메일 형식입니다.');
      } else if (e.code == 'user-not-found') {
        _showAlert('등록되지 않은 사용자입니다.');
      } else {
        _showAlert('오류가 발생했습니다.');
      }
    }

    isLoading = false;
    notifyListeners();
  }

  /// 오류 snackbar
  void _showAlert(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        duration: const Duration(seconds: 1),
        content: Text(message),
        backgroundColor: Palette.error,
      ),
    );
  }

  /// 성공시 complete_reset_screen으로 이동
  void _success() {
    if (context.mounted) {
      context.go('/sign-in/complete_password_reset');
    }
  }
}

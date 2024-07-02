import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:structure/components/custom_pop_up.dart';
import 'package:structure/config/pallete.dart';
import 'package:structure/model/user_model.dart';

class PasswordResetViewModel with ChangeNotifier {
  UserModel userModel;
  PasswordResetViewModel({required this.userModel});

  final formKey = GlobalKey<FormState>();
  bool isLoading = false;

  TextEditingController email = TextEditingController();

  // 모든 값이 올바르게 입력됐는지 확인
  bool isAllValid() {
    return true;
  }

  late BuildContext _context;

  /// 비밀번호 변경
  Future<void> sendResetPassword(BuildContext context) async {
    _context = context;
    isLoading = true;
    notifyListeners();

    try {
      await FirebaseAuth.instance.sendPasswordResetEmail(email: email.text);
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
    ScaffoldMessenger.of(_context).showSnackBar(
      SnackBar(
        duration: const Duration(seconds: 1),
        content: Text(message),
        backgroundColor: Palette.alertBg,
      ),
    );
  }

  void _success() {
    showSuccessChangeUserInfo(_context);
    email.clear();
  }
}

import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:structure/components/custom_pop_up.dart';
import 'package:structure/config/pallete.dart';
import 'package:structure/model/user_model.dart';
import 'package:structure/config/labels.dart';

class ChangePasswordViewModel with ChangeNotifier {
  UserModel userModel;
  ChangePasswordViewModel({required this.userModel});

  final formKey = GlobalKey<FormState>();
  bool isLoading = false;
  bool isActivateButton = false;

  TextEditingController originPW = TextEditingController();
  TextEditingController newPW = TextEditingController();
  TextEditingController newCPW = TextEditingController();

  // 버튼 활성화 확인을 위한 변수
  bool _isValidPw = false;
  bool _isValidNewPw = false;
  bool _isValidCPw = false;

  /// 기존 비밀번호 유효성 검사
  String? pwValidate(String? value) {
    if (value!.isEmpty) {
      _isValidPw = false;
      return '비밀번호를 입력하세요.';
    } else {
      _isValidPw = true;
      return null;
    }
  }

  /// 비밀번호 유효성 검사
  String? newPwValidate(String? value) {
    // 비어있지 않고 비밀번호 형식에 맞지 않을 때, 빨간 에러 메시지
    final bool isValid = _validatePassword(value!);
    if (value.isNotEmpty && !isValid) {
      _isValidNewPw = false;
      return Labels.pwdErrorStr;
    } else if (value.isEmpty) {
      _isValidNewPw = false;
      return null;
    } else {
      _isValidNewPw = true;
      return null;
    }
  }

  /// 비밀번호 재입력 유효성 검사
  String? cPwValidate(String? value) {
    // 비어있지 않고 비밀번호와 같지 않을 때, 빨간 에러 메시지
    if (value!.isNotEmpty && value != newPW.text) {
      _isValidCPw = false;
      return Labels.pwdNotSame;
    } else if (value.isEmpty) {
      _isValidCPw = false;
      return null;
    } else {
      _isValidCPw = true;
      return null;
    }
  }

  /// 비밀번호 유효성 검사
  bool _validatePassword(String password) {
    // 비밀번호 유효성을 검사하는 정규식
    const pattern = Labels.pwdPattern;
    final regex = RegExp(pattern);
    isActivateButton = true; //버튼 활성화
    notifyListeners();
    return regex.hasMatch(password);
  }

  /// 모든 값이 올바르게 입력됐는지 확인
  bool isAllValid() {
    if (_isValidPw && _isValidNewPw && _isValidCPw) {
      return true;
    } else {
      return false;
    }
  }

  late BuildContext _context;

  /// 비밀번호 변경 함수
  Future<void> changePassword(BuildContext context) async {
    _context = context;
    isLoading = true;
    notifyListeners();
    try {
      // 기존 firebase user 정보 불러오기 (현재 로그인된 유저)
      User? user = FirebaseAuth.instance.currentUser;
      if (user != null) {
        // 비밀번호 변경 전 firebase에 재인증 필요
        await FirebaseAuth.instance.currentUser?.reauthenticateWithCredential(
          EmailAuthProvider.credential(
            email: userModel.userId!,
            password: originPW.text,
          ),
        );
        await user.updatePassword(newPW.text); // Firebase update password
        _success();
      } else {
        throw ErrorDescription('User does not exist');
      }
    } on FirebaseException catch (e) {
      debugPrint('error: ${e.code}');
      if (e.code == 'wrong-password') {
        _showAlert('현재 비밀번호가 일치하지 않습니다.'); // 기존 비밀번호가 틀리면 alert 생성
      } else {
        _showAlert('오류가 발생했습니다.');
      }
    } catch (e) {
      debugPrint('Error: $e');
      if (context.mounted) showErrorPopup(context);
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
        backgroundColor: Pallete.alertBg,
      ),
    );
  }

  /// 비밀번호 변경 성공
  void _success() {
    showSuccessChangeUserInfo(_context, null);
    originPW.clear();
    newPW.clear();
    newCPW.clear();
    _isValidPw = false;
    _isValidNewPw = false;
    _isValidCPw = false;
  }
}

import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:structure/config/labels.dart';
import 'package:structure/config/pallete.dart';
import 'package:structure/dataSource/local_data_source.dart';
import 'package:structure/dataSource/remote_data_source.dart';
import 'package:structure/model/user_model.dart';

class DeleteUserViewModel with ChangeNotifier {
  UserModel userModel;
  DeleteUserViewModel({required this.userModel});

  final formKey = GlobalKey<FormState>();
  bool isLoading = false;

  TextEditingController password = TextEditingController();

  bool _isValidPw = false;

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

  /// 값이 올바르게 입력됐는지 확인
  bool isValid() {
    if (_isValidPw) {
      return true;
    } else {
      return false;
    }
  }

  late BuildContext _context;

  /// 회원 탈퇴 함수
  Future<void> deleteUser(BuildContext context) async {
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
            password: password.text,
          ),
        );

        // Firebase 유저 삭제
        // await user.delete();

        // DB에서 유저 삭제 API 호출
        final response = await RemoteDataSource.deleteUser(userModel.userId!);
        if (response == null) {
          throw Error();
        }

        _success();
      } else {
        print('User does not exist.');
      }
    } on FirebaseException catch (e) {
      print('error: ${e.code}');
      if (e.code == 'wrong-password') {
        _showAlert(Labels.pwdNotSame); // 기존 비밀번호가 틀리면 alert 생성
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

  /// 비밀번호 변경 성공
  void _success() async {
    password.clear();
    await LocalDataSource.deleteLocalData(userModel.userId!);
    if (_context.mounted) _context.go('/sign-in');
    _showAlert('회원 탈퇴가 성공적으로 처리되었습니다.');
  }
}

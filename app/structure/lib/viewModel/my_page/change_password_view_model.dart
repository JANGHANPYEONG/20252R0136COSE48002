import 'dart:convert';

import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:structure/components/custom_pop_up.dart';
import 'package:structure/config/pallete.dart';
import 'package:structure/dataSource/remote_data_source.dart';
import 'package:structure/model/user_model.dart';
import 'package:structure/config/labels.dart';

class ChangePasswordViewModel with ChangeNotifier {
  UserModel userModel;
  ChangePasswordViewModel({required this.userModel});

  final formKey = GlobalKey<FormState>();
  bool isLoading = false;

  TextEditingController originPW = TextEditingController();
  TextEditingController newPW = TextEditingController();
  TextEditingController newCPW = TextEditingController();

  // 버튼 활성화 확인을 위한 변수
  bool _isValidPw = false;
  bool _isValidNewPw = false;
  bool _isValidCPw = false;

  // 기존 비밀번호 유효성 검사
  String? pwValidate(String? value) {
    if (value!.isEmpty) {
      _isValidPw = false;
      return null;
    } else {
      _isValidPw = true;
      return null;
    }
  }

  // 비밀번호 유효성 검사
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

  // 비밀번호 재입력 유효성 검사
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

  // 비밀번호 유효성 검사
  bool _validatePassword(String password) {
    // 비밀번호 유효성을 검사하는 정규식
    const pattern =
        r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[!@#$%^&*()\-_=+{};:,<.>]).{10,}$';
    final regex = RegExp(pattern);

    return regex.hasMatch(password);
  }

  // 모든 값이 올바르게 입력됐는지 확인
  bool isAllValid() {
    if (_isValidPw && _isValidNewPw && _isValidCPw) {
      return true;
    } else {
      return false;
    }
  }

  late BuildContext _context;

  // 비밀번호 변경
  Future<void> changePassword(BuildContext context) async {
    isLoading = true;
    notifyListeners();
    try {
      final response = await RemoteDataSource.checkUserPw(_userInfoToJson());

      _context = context;
      if (response == null) {
        _showAlert();
        isLoading = false;
        notifyListeners();
        return;
      }

      User? user = FirebaseAuth.instance.currentUser;
      if (user != null) {
        final response =
            await RemoteDataSource.changeUserPw(_convertChangeUserPwToJson());
        if (response == null) {
          throw Error();
        }
        await FirebaseAuth.instance.currentUser?.reauthenticateWithCredential(
          EmailAuthProvider.credential(
            email: userModel.userId!,
            password: originPW.text,
          ),
        );
        await user.updatePassword(newPW.text);
        _context = context;
        _success();
      } else {
        print('User does not exist.');
      }
    } catch (e) {
      print('error: $e');
    }
    isLoading = false;
    notifyListeners();
  }

  // 유저 비밀번호 확인
  String _userInfoToJson() {
    return jsonEncode({
      "userId": userModel.userId,
      "password": originPW.text,
    });
  }

  // 유저 비밀번호 변경 시 반환
  String _convertChangeUserPwToJson() {
    return jsonEncode({
      "userId": userModel.userId,
      "password": newPW.text,
    });
  }

  void _showAlert() {
    ScaffoldMessenger.of(_context).showSnackBar(
      const SnackBar(
        duration: Duration(seconds: 1),
        content: Text(
          '비밀번호를 확인하세요',
        ),
        backgroundColor: Palette.alertBg,
      ),
    );
  }

  void _success() {
    showSuccessChangeUserInfo(_context);
    originPW.clear();
    newPW.clear();
    newCPW.clear();
    _isValidPw = false;
    _isValidNewPw = false;
    _isValidCPw = false;
  }
}

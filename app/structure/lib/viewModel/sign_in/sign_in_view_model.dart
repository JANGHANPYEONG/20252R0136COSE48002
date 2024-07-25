import 'dart:convert';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:structure/config/pallete.dart';
import 'package:structure/dataSource/local_data_source.dart';
import 'package:structure/dataSource/remote_data_source.dart';
import 'package:structure/model/meat_model.dart';
import 'package:structure/model/user_model.dart';

class SignInViewModel with ChangeNotifier {
  UserModel userModel;
  MeatModel meatModel;
  SignInViewModel({required this.userModel, required this.meatModel});

  String userId = '';
  String userPw = '';
  bool isLoading = false;
  bool isAutoLogin = false;

  void autoLoginCheck(BuildContext context) {
    if (userModel.auto) {
      context.go('/home');
    }
  }

  final formKey = GlobalKey<FormState>();

  // firbase authentic
  final _authentication = FirebaseAuth.instance;

  late BuildContext _context;

  // 자동로그인 버튼 클릭 시
  void clickedAutoLogin(bool value) {
    isAutoLogin = value;
    notifyListeners();
  }

  // 로그인 버튼 클릭 시
  Future<void> clickedSignInButton(BuildContext context) async {
    FocusScope.of(context).unfocus();
    await _signIn(context);
  }

  // 로그인 진행
  Future<void> _signIn(BuildContext context) async {
    // 로딩 상태를 활성화
    isLoading = true;
    notifyListeners();

    try {
      // 로그인 시도
      await _authentication.signInWithEmailAndPassword(
        email: userId,
        password: userPw,
      );

      // 이메일 validation
      // 이메일 인증을 위해서 필요
      final bool isValidEmail = await validateEmail();

      if (!isValidEmail) {
        // 이메일 invalid
        _authentication.signOut();
        throw InvalidEmailException('이메일 인증을 완료하세요.');
      } else {
        // 이메일 valid
        // DB에서 로그인하는 사용자 정보 불러와서 로컬 스토리지에 저장
        if (await saveUserInfo()) {
          // 자동 로그인 설정
          if (isAutoLogin) {
            await LocalDataSource.saveDataToLocal(
                jsonEncode({'auto': userModel.userId}), 'auto.json');
          } else {
            await LocalDataSource.saveDataToLocal(
                jsonEncode({'auto': null}), 'auto.json');
          }

          // 로딩 상태를 비활성화
          isLoading = false;
          notifyListeners();

          // 페이지 이동
          _context = context;
          _movePage();
        } else {
          throw Error();
        }
      }
    } catch (e) {
      // 예외 처리
      String errorMessage;
      if (e is FirebaseException) {
        // 로그인 실패
        if (e.code == 'user-not-found') {
          errorMessage = '존재하지 않는 아이디입니다.';
        } else {
          errorMessage = '아이디와 비밀번호를 확인하세요.';
        }
      } else if (e is InvalidEmailException) {
        // 이메일 인증 미완료
        errorMessage = e.message;
      } else {
        // 기타 오류
        errorMessage = '오류가 발생했습니다.';
      }

      // 로딩 상태를 비활성화
      isLoading = false;
      notifyListeners();

      // 에러 스낵바
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            duration: const Duration(seconds: 1),
            content: Text(errorMessage),
            backgroundColor: Palette.alertBg,
          ),
        );
      }

      return;
    }
  }

  /// firebase에서 유저 이메일 유효한지 검사
  Future<bool> validateEmail() async {
    try {
      User? user = FirebaseAuth.instance.currentUser;
      await user!.reload();
      if (user.emailVerified) {
        return true;
      }
    } catch (e) {
      debugPrint('인증 실패');
      return false;
    }
    return false;
  }

  /// 유저 정보 저장
  Future<bool> saveUserInfo() async {
    // 로그인 API 호출
    try {
      // 유저 정보 가져오기 시도
      dynamic userInfo = await RemoteDataSource.login(userId)
          .timeout(const Duration(seconds: 10));
      if (userInfo is Map<String, dynamic>) {
        // 200 OK
        // 데이터 fetch
        userModel.fromJson(userInfo);
        // 육류 정보 생성자 id 저장
        meatModel.userId = userModel.userId;
        return true;
      } else {
        throw ErrorDescription(userInfo);
      }
    } catch (e) {
      debugPrint('Error: $e');
      // TODO : 에러 메시지 팝업
      return false;
    }
  }

  void _movePage() {
    _context.go('/home');
  }
}

// 이메일 인증 예외 처리
class InvalidEmailException implements Exception {
  final String message;
  InvalidEmailException(this.message);

  @override
  String toString() {
    return 'InvalidEmailException: $message';
  }
}

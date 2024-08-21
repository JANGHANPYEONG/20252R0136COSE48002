import 'dart:convert';

import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:structure/components/custom_dialog.dart';
import 'package:structure/config/usefuls.dart';
import 'package:structure/dataSource/local_data_source.dart';
import 'package:structure/model/user_model.dart';

class MyPageViewModel with ChangeNotifier {
  UserModel userModel;
  BuildContext context;

  MyPageViewModel(this.userModel, this.context) {
    _initialize();
  }

  String userId = ''; // 사용자 id
  String userName = ''; // 사용자 이름
  String homeAdress = '-'; // 주소
  String company = '-'; // 회사명
  String department = '-'; // 부서명
  String jobTitle = '-'; // 직위
  String userType = ''; // 권한 type (Normal, Researcher, Manager)
  String createdAt = ''; // 가입 날짜

  void _initialize() {
    userId = userModel.userId ?? '-';
    userName = userModel.name ?? '-';
    userType = userModel.type ?? '-';
    createdAt = Usefuls.parseDate(userModel.createdAt);
    if (userModel.homeAdress != null && userModel.homeAdress!.isNotEmpty) {
      int index = userModel.homeAdress!.indexOf('/');
      if (index != -1 && userModel.homeAdress!.substring(0, index).isNotEmpty) {
        homeAdress = userModel.homeAdress!.substring(0, index);
      }
      if (index != -1 &&
          userModel.homeAdress!.substring(index + 1).isNotEmpty) {
        homeAdress += ' ${userModel.homeAdress!.substring(index + 1)}';
      }
    }
    if (userModel.company != null && userModel.company!.isNotEmpty) {
      company = userModel.company!;
    }
    if (userModel.jobTitle != null && userModel.jobTitle!.isNotEmpty) {
      int index = userModel.jobTitle!.indexOf('/');
      if (index != -1 && userModel.jobTitle!.substring(0, index).isNotEmpty) {
        department = userModel.jobTitle!.substring(0, index);
      }
      if (index != -1 && userModel.jobTitle!.substring(index + 1).isNotEmpty) {
        jobTitle = userModel.jobTitle!.substring(index + 1);
      }
    }
  }

  /// 로그아웃 버튼 클릭
  Future<void> clickedSignOut() async {
    showLogoutDialog(context, logoutCancel, logout);
  }

  /// 로그아웃 팝업 취소 클릭
  void logoutCancel() {
    context.pop();
  }

  /// 로그아웃 팝업 로그아웃 클릭
  void logout() async {
    await FirebaseAuth.instance.signOut();
    await LocalDataSource.saveDataToLocal(
        jsonEncode({'auto': null}), 'auto.json');
    userModel.reset();
    if (context.mounted) {
      context.go('/sign-in');
    }
  }

  /// 상세 정보 변경 클릭
  void clickedEdit() async {
    await GoRouter.of(context)
        .push('/home/my-page/user-detail')
        .then((_) => _initialize());
    notifyListeners();
  }

  /// 비밀번호 변경 클릭
  void clickedChangePW() {
    context.go('/home/my-page/change-pw');
  }

  /// 회원 탈퇴 클릭
  void clickedDeleteUser() {
    context.go('/home/my-page/delete-user');
  }
}

//
//
// 육류 이미지 페이지(수정 불가!) : ViewModel
//
//

import 'dart:io';

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:structure/dataSource/remote_data_source.dart';
import 'package:structure/model/meat_model.dart';
import 'package:structure/model/user_model.dart';

class InsertionMeatImageNotEditableViewModel with ChangeNotifier {
  final MeatModel meatModel;
  final UserModel userModel;
  final int imageIdx;

  InsertionMeatImageNotEditableViewModel(
      this.meatModel, this.userModel, this.imageIdx) {
    fetchDate(meatModel.freshmeat!['createdAt']!);
    imagePath = meatModel.imagePath;
    date = '${time.year}.${time.month}.${time.day}';
    getName();
  }

  String date = '-';
  String userName = '-';

  late DateTime time;
  File? pickedImage;
  String? imagePath;
  bool isLoading = false;

  void getName() async {
    if (meatModel.freshmeat!['userId'] == userModel.userId) {
      // 로그인된 유저와 id가 같으면 그냥 userModel에서 이름 불러오기
      userName = userModel.name ?? '-';
    } else {
      // 다른 유저면 api 호출해서 이름 정보 가져오기
      dynamic user =
          await RemoteDataSource.getUserInfo(meatModel.freshmeat!['userId']);
      userName = user['name'] ?? '-';
    }
  }

  // 초기 이미지 할당.
  void fetchDate(String dateString) {
    DateTime? date = _parseDate(dateString);
    print(dateString);
    if (date != null) {
      time = date;
    } else {
      print('DateString format is not valid.');
    }
  }

  // Date Parsing
  DateTime? _parseDate(String dateString) {
    try {
      return DateTime.parse(dateString);
    } catch (e) {
      return null;
    }
  }

  void clickedNextButton(BuildContext context) {
    context.go('/home/data-manage-normal/edit');
  }
}

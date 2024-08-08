//
//
// 가열육 추가 데이터 입력 (viewNodel) : Researcher
//
//

import 'package:flutter/material.dart';
import 'package:structure/config/userfuls.dart';
import 'package:structure/main.dart';
import 'package:structure/model/meat_model.dart';
import 'package:structure/model/user_model.dart';

class InsertionHeatedSensoryAddViewModel with ChangeNotifier {
  final MeatModel meatModel;
  final UserModel userModel;
  InsertionHeatedSensoryAddViewModel(this.meatModel, this.userModel) {
    _initialize();
  }

  bool isLoading = false;

  //날짜
  String processCreatedAt = '';
  DateTime currentDate = DateTime.now();
  //연도 기본 값
  double tenderness = 1;

  void _initialize() {
    // print("meatmodel 추ㅏㄱ");
    // print(meatModel);
    print("----------heatedSensoryEval---------");
    // print(meatModel.heatedSensoryEval!["createdAt"]);
    processCreatedAt =
        Usefuls.parseDate(meatModel.heatedSensoryEval?['createdAt']);
    print(processCreatedAt);

    notifyListeners();
  }

  void calculateDate() {}
}

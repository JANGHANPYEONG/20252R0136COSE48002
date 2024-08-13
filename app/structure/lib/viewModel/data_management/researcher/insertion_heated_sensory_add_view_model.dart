//
//
// 가열육 추가 데이터 입력 (viewNodel) : Researcher
//
//

import 'package:flutter/material.dart';
import 'package:structure/model/meat_model.dart';
import 'package:structure/model/user_model.dart';

class InsertionHeatedSensoryAddViewModel with ChangeNotifier {
  final MeatModel meatModel;
  final UserModel userModel;
  InsertionHeatedSensoryAddViewModel(this.meatModel, this.userModel) {
    _initialize();
  }

  bool isLoading = false;
  int? seqNo = 0;

  //날짜
  String processCreatedAt = '';
  // String currentDate = Usefuls.parseDate(Usefuls.getCurrentDate());
  DateTime currentDate = DateTime.now();
  int dateDiff = -1;

  //딥에이징 등록 후 3, 7, 14, 21일 각각 경과 했는지 여부
  List<bool> checkDate = [false, false, false, false];

  //딥에이징 등록 후 3, 7, 14, 21일차인지 여부
  bool check = false;
  //연도 기본 값
  double tenderness = 1;

  void _initialize() {
    seqNo = meatModel.seqno;
    print(meatModel.deepAgingInfo);
    print(seqNo);
    processCreatedAt = meatModel.deepAgingCreatedAt!;
    print(processCreatedAt);
    print("길이 : ${meatModel.deepAgingInfo!.length}");
    print("1111");
    calculateDiff();
    print("22222");
    checkTenderness();
    print("333333");
    checkDateBool();
    notifyListeners();
  }

  void deepAging() {}

  /// 현재 날짜 - 딥에이징 등록 날짜 구하는 함수
  void calculateDiff() {
    dateDiff = int.parse(currentDate
        .difference(DateTime.parse(processCreatedAt))
        .inDays
        .toString());
    // print("dateDiff :::: $dateDiff");
    notifyListeners();
  }

  void checkTenderness() {
    if (dateDiff >= 3) {
      check = true;
      notifyListeners();
    }
    print("Dcdlc");
    print(check);
  }

  void checkDateBool() {
    print("dateDiff : :$dateDiff");
    if (dateDiff >= 21) {
      checkDate[0] = true;
      checkDate[1] = true;
      checkDate[2] = true;
      checkDate[3] = true;
    } else if (dateDiff >= 14) {
      checkDate[0] = true;
      checkDate[1] = true;
      checkDate[2] = true;
    } else if (dateDiff >= 7) {
      checkDate[0] = true;
      checkDate[1] = true;
    } else if (dateDiff >= 3) {
      checkDate[0] = true;
    }
    print("ddd");
    print(checkDate);
    notifyListeners();
  }
}

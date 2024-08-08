//
//
// 가열육 추가 데이터 입력 (viewNodel) : Researcher
//
//

import 'package:flutter/material.dart';
import 'package:structure/config/usefuls.dart';
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
  String currentDate = Usefuls.parseDate(Usefuls.getCurrentDate());
  int dateDiff = -1;

  //딥에이징 등록 후 3, 7, 14, 21일차인지 여부
  bool check = false;
  //연도 기본 값
  double tenderness = 1;

  void _initialize() {
    print("----------deepaginginfo---------");
    print(meatModel.deepAgingInfo);
    // processCreatedAt =
    //     Usefuls.parseDate(meatModel.heatedSensoryEval?['createdAt']);
    seqNo = meatModel.seqno;
    print(meatModel.deepAgingInfo![seqNo!]['date']);
    processCreatedAt = meatModel.deepAgingInfo![seqNo!]['date'];
    calculateDiff();
    checkTenderness();
    notifyListeners();
  }

  void calculateDiff() {
    dateDiff = int.parse(Usefuls.dotDateToDate(currentDate)) -
        int.parse(processCreatedAt);
    notifyListeners();
    // print(dateDiff);
  }

  void checkTenderness() {
    if (dateDiff == 3 || dateDiff == 7 || dateDiff == 14 || dateDiff == 21) {
      check = true;
      notifyListeners();
    }
  }
}

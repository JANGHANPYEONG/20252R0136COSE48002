//
//
// 가열육 추가 데이터 입력 (viewNodel) : Researcher
//
//

import 'package:flutter/material.dart';
import 'package:structure/dataSource/remote_data_source.dart';
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
  double tenderness3 = 1;
  double tenderness7 = 1;
  double tenderness14 = 1;
  double tenderness21 = 1;

  void _initialize() {
    seqNo = meatModel.seqno;
    processCreatedAt = meatModel.deepAgingCreatedAt!;
    calculateDiff();
    checkTenderness();
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

  void onChangedTenderness3(dynamic value) {
    tenderness3 = double.parse(value.toStringAsFixed(1));
    notifyListeners();
  }

  void onChangedTenderness7(dynamic value) {
    tenderness7 = double.parse(value.toStringAsFixed(1));
    notifyListeners();
  }

  void onChangedTenderness14(dynamic value) {
    tenderness14 = double.parse(value.toStringAsFixed(1));
    notifyListeners();
  }

  void onChangedTenderness21(dynamic value) {
    tenderness21 = double.parse(value.toStringAsFixed(1));
    notifyListeners();
  }

  Future<void> saveData(BuildContext context) async {
    bool isPost = false;
    if (meatModel.heatedSensoryEval == null) {
      isPost = true;
      meatModel.heatedSensoryEval = {};
      meatModel.heatedSensoryEval!['meatId'] = meatModel;
      meatModel.heatedSensoryEval!['seqno'] = meatModel.seqno;
      meatModel.heatedSensoryEval!['userId'] = userModel.userId;
    }

    meatModel.heatedSensoryEval!['tenderness3'] = tenderness3;
    meatModel.heatedSensoryEval!['tenderness7'] = tenderness7;
    meatModel.heatedSensoryEval!['tenderness14'] = tenderness14;
    meatModel.heatedSensoryEval!['tenderness21'] = tenderness21;

    // try{
    //   dynamic response;
    //   if(isPost){
    //     response = await RemoteDataSource.createMeatData(dest, jsonData)
    //   }
    // }
  }
}

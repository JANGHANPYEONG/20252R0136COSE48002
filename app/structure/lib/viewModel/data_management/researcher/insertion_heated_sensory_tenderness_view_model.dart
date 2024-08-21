//
//
// 가열육 연도 추가 데이터 입력 (viewNodel) : Researcher
//
//

import 'package:flutter/material.dart';
import 'package:structure/model/meat_model.dart';
import 'package:structure/model/user_model.dart';

class InsertionHeatedSensoryTendernessViewModel with ChangeNotifier {
  final MeatModel meatModel;
  final UserModel userModel;
  InsertionHeatedSensoryTendernessViewModel(this.meatModel, this.userModel) {
    _initialize();
  }

  bool isLoading = false;
  int? seqno = 0;

  // 날짜
  String processCreatedAt = '';
  DateTime currentDate = DateTime.now();
  int dateDiff = -1;

  // 딥에이징 등록 후 3, 7, 14, 21일 각각 경과 했는지 여부
  List<bool> checkDate = [false, false, false, false];

  // 딥에이징 등록 후 3, 7, 14, 21일차인지 여부
  bool check = false;

  // 연도 기본 값
  double tenderness3 = 1.0;
  double tenderness7 = 1.0;
  double tenderness14 = 1.0;
  double tenderness21 = 1.0;

  void _initialize() {
    seqno = meatModel.seqno;
    processCreatedAt = meatModel.deepAgingCreatedAt!;
    tenderness3 =
        double.parse('${meatModel.heatedSensoryEval?['tenderness3'] ?? 1.0}');
    tenderness7 =
        double.parse('${meatModel.heatedSensoryEval?['tenderness7'] ?? 1.0}');
    tenderness14 =
        double.parse('${meatModel.heatedSensoryEval?['tenderness14'] ?? 1.0}');
    tenderness21 =
        double.parse('${meatModel.heatedSensoryEval?['tenderness21'] ?? 1.0}');

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
    notifyListeners();
  }

  void checkTenderness() {
    if (dateDiff >= 3) {
      check = true;
      notifyListeners();
    }
  }

  void checkDateBool() {
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
    notifyListeners();
  }

  void onChangedTenderness3(dynamic value) {
    tenderness3 = double.parse(value.toStringAsFixed(1));
    meatModel.heatedSensoryEval!['tenderness3'] = tenderness3;
    notifyListeners();
  }

  void onChangedTenderness7(dynamic value) {
    tenderness7 = double.parse(value.toStringAsFixed(1));
    meatModel.heatedSensoryEval!['tenderness7'] = tenderness7;
    notifyListeners();
  }

  void onChangedTenderness14(dynamic value) {
    tenderness14 = double.parse(value.toStringAsFixed(1));
    meatModel.heatedSensoryEval!['tenderness14'] = tenderness14;
    notifyListeners();
  }

  void onChangedTenderness21(dynamic value) {
    tenderness21 = double.parse(value.toStringAsFixed(1));
    meatModel.heatedSensoryEval!['tenderness21'] = tenderness21;
    notifyListeners();
  }
}

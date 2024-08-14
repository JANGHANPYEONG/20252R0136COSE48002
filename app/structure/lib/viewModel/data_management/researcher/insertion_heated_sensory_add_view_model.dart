//
//
// 가열육 추가 데이터 입력 (viewNodel) : Researcher
//
//

import 'package:flutter/material.dart';
import 'package:structure/components/custom_pop_up.dart';
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
  // late BuildContext _context;
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
  num tenderness3 = 1.0;
  num tenderness7 = 1.0;
  num tenderness14 = 1.0;
  num tenderness21 = 1.0;

  void _initialize() {
    print("시작");
    seqNo = meatModel.seqno;
    processCreatedAt = meatModel.deepAgingCreatedAt!;
    print("aaaaa");
    print(meatModel.heatedSensoryEval);
    tenderness3 = meatModel.heatedSensoryEval?['tenderness3'] ?? 1.0;
    print("dfs");
    tenderness7 = meatModel.heatedSensoryEval?['tenderness7'] ?? 1.0;
    tenderness14 = meatModel.heatedSensoryEval?['tenderness14'] ?? 1.0;
    tenderness21 = meatModel.heatedSensoryEval?['tenderness21'] ?? 1.0;

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
    meatModel.heatedSensoryEval!['tenderness3'] = tenderness3;
    meatModel.heatedSensoryEval!['tenderness7'] = tenderness7;
    meatModel.heatedSensoryEval!['tenderness14'] = tenderness14;
    meatModel.heatedSensoryEval!['tenderness21'] = tenderness21;

    try {
      dynamic response;
      response = await RemoteDataSource.patchMeatData(
          'heatedmeat-eval', meatModel.toJsonHeatedSensory());
      if (response == 200) {
        meatModel.updateHeatedSeonsory();
        // _context = context;
      } else {
        throw ErrorDescription(response);
      }
    } catch (e) {
      debugPrint('Error: $e');
      if (context.mounted) showErrorPopup(context);
    }
    meatModel.checkCompleted();
    isLoading = false;
    notifyListeners();
  }
}

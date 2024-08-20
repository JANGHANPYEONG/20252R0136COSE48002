//
//
// 가열육 관능평가(ViewModel) : Researcher
//
//

import 'package:flutter/widgets.dart';
import 'package:go_router/go_router.dart';
import 'package:structure/components/custom_pop_up.dart';
import 'package:structure/dataSource/remote_data_source.dart';
import 'package:structure/model/meat_model.dart';
import 'package:structure/model/user_model.dart';

class InsertionHeatedSensoryViewModel with ChangeNotifier {
  final MeatModel meatModel;
  final UserModel userModel;
  InsertionHeatedSensoryViewModel(this.meatModel, this.userModel) {
    _initialize();
  }
  bool isLoading = false;

  // 관능평가 값
  // 초기 값은 1(최하)로 설정
  num flavor = 1;
  num juiciness = 1;
  num tenderness0 = 1;
  // double tenderness3 = 1;
  // double tenderness7 = 1;
  // double tenderness14 = 1;
  // double tenderness21 = 1;

  num umami = 1;
  num palatability = 1;
  // num palabilityrgs = 1;
  // 초기 할당 (객체에 값이 존재시 할당)
  void _initialize() {
    flavor = meatModel.heatedSensoryEval?['flavor'] ?? 1;
    juiciness = meatModel.heatedSensoryEval?['juiciness'] ?? 1;
    tenderness0 = meatModel.heatedSensoryEval?['tenderness0'] ?? 1;
    umami = meatModel.heatedSensoryEval?['umami'] ?? 1;
    palatability = meatModel.heatedSensoryEval?['palatability'] ?? 1;
    notifyListeners();
  }

  /// 관능평가 풍미 데이터 할당
  void onChangedFlavor(dynamic value) {
    flavor = double.parse(value.toStringAsFixed(1));
    notifyListeners();
  }

  /// 관능평가 다즙성 데이터 할당
  void onChangedJuiciness(dynamic value) {
    juiciness = double.parse(value.toStringAsFixed(1));
    notifyListeners();
  }

  /// 관능평가 연도 데이터 할당
  void onChangedTenderness(dynamic value) {
    tenderness0 = double.parse(value.toStringAsFixed(1));
    notifyListeners();
  }

  /// 관능평가 표면육즙 데이터 할당
  void onChangedUmami(dynamic value) {
    umami = double.parse(value.toStringAsFixed(1));
    notifyListeners();
  }

  /// 관능평가 기호도 데이터 할당
  void onChangedPalatability(dynamic value) {
    palatability = double.parse(value.toStringAsFixed(1));
    notifyListeners();
  }

  // 데이터를 객체에 할당 (이후 POST)
  Future<void> saveData(BuildContext context) async {
    isLoading = true;
    notifyListeners();

    // heatedSensoryEval이 없으면 post로 진행해야 함
    bool isPost = false;

    if (meatModel.heatedSensoryEval == null) {
      // POST의 경우 신규 데이터 생성
      isPost = true;

      meatModel.heatedSensoryEval = {};
      meatModel.heatedSensoryEval!['meatId'] = meatModel.meatId;
      meatModel.heatedSensoryEval!['seqno'] = meatModel.seqno;
      meatModel.heatedSensoryEval!['userId'] = userModel.userId;
    }
    // 가열육 관능평가 데이터 입력
    meatModel.heatedSensoryEval!['flavor'] = flavor;
    meatModel.heatedSensoryEval!['juiciness'] = juiciness;
    meatModel.heatedSensoryEval!['tenderness0'] = tenderness0;
    meatModel.heatedSensoryEval!['umami'] = umami;
    meatModel.heatedSensoryEval!['palatability'] = palatability;

    try {
      dynamic response;

      if (isPost) {
        response = await RemoteDataSource.createMeatData(
            'heatedmeat-eval', meatModel.toJsonHeatedSensory());
      } else {
        response = await RemoteDataSource.patchMeatData(
            'heatedmeat-eval', meatModel.toJsonHeatedSensory());
      }

      if (response == 200) {
        meatModel.updateHeatedSeonsory();
      } else {
        // TODO : 입력한 데이터 초기화
        throw ErrorDescription(response);
      }
    } catch (e) {
      debugPrint('Error: $e');
      if (context.mounted) showErrorPopup(context);
    }

    meatModel.checkCompleted();

    isLoading = false;
    notifyListeners();

    if (context.mounted) context.pop();
  }

  void clickedTendernessAdd(BuildContext context) {
    context.go(
        '/home/data-manage-researcher/add/processed-meat/heated-sensory/heated-sensory-add');
  }
}

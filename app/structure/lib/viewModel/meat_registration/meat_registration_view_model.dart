//
//
// 육류 등록 viewModel.
//
//

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:structure/components/custom_dialog.dart';
import 'package:structure/components/custom_pop_up.dart';
import 'package:structure/dataSource/local_data_source.dart';
import 'package:structure/model/meat_model.dart';
import 'package:structure/model/user_model.dart';

class MeatRegistrationViewModel with ChangeNotifier {
  MeatModel meatModel;
  UserModel userModel;
  BuildContext context;

  MeatRegistrationViewModel({
    required this.meatModel,
    required this.userModel,
    required this.context,
  });
  bool isLoading = false;

  void initialize() {
    // 육류 인스턴스 초기화
    meatModel.reset();

    // 육류 기본 생성은 seqno: 0
    meatModel.seqno = 0;

    // 임시저장 데이터 fetch
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      await checkTempData();
    });
  }

  /// 임시저장 데이터 check
  Future<void> checkTempData() async {
    try {
      dynamic response = await LocalDataSource.getLocalData(meatModel.userId!);
      if (response == null) {
        throw Error();
      } else {
        await _showTempDataDialog(response);
      }
    } catch (e) {
      debugPrint('Error: $e');
      if (context.mounted) showErrorPopup(context, error: e.toString());
    }
  }

  /// 임시저장 dialog : 임시 데이터 존재시 결정하는 팝업 생성
  Future<void> _showTempDataDialog(dynamic response) async {
    showDataRegisterDialog(
      context,
      () async {
        try {
          // 처음부터 등록
          await LocalDataSource.deleteLocalData(meatModel.userId!);
          notifyListeners();
          if (context.mounted) context.pop();
        } catch (e) {
          debugPrint('Error: $e');
          if (context.mounted) showErrorPopup(context, error: e.toString());
        }
      },
      () async {
        // 이어서 등록
        meatModel.fromJsonTemp(response);
        notifyListeners();
        context.pop();
      },
    );
  }

  /// STEP 1 : 육류 기본정보 등록
  void clickedBasic() {
    context.go('/home/registration/trace-num');
  }

  /// STEP 2 : 육류 단면 촬영
  void clickedImage() {
    if (meatModel.basicCompleted) context.go('/home/registration/image');
  }

  /// STEP 3 : 원육 관능평가
  void clickedFreshmeat() {
    if (meatModel.imageCompleted) context.go('/home/registration/freshmeat');
  }

  /// 모든 데이터 입력이 완료됐는지 확인하는 함수
  bool checkAllCompleted() {
    return meatModel.basicCompleted &&
        meatModel.imageCompleted &&
        meatModel.sensoryCompleted;
  }

  /// 관리번호 생성 버튼
  void clickCreateBtn() async {
    // 페이지 이동
    if (context.mounted) context.go('/home/success-registration');
  }

  /// 임시저장 버튼
  Future<void> clickedTempSaveButton() async {
    try {
      dynamic response = await LocalDataSource.saveDataToLocal(
          meatModel.toJsonTemp(), meatModel.userId!);
      if (response == null) throw Error();
      if (context.mounted) showTemporarySavePopup(context);
    } catch (e) {
      debugPrint('Error: $e');
      if (context.mounted) showErrorPopup(context, error: e.toString());
    }
  }
}

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

  MeatRegistrationViewModel({
    required this.meatModel,
    required this.userModel,
  });
  bool isLoading = false;

  void initialize(BuildContext context) {
    // 육류 인스턴스 초기화
    meatModel.reset();

    // 육류 기본 생성은 seqno: 0
    meatModel.seqno = 0;

    // 임시저장 데이터 fetch
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      await checkTempData(context);
    });
  }

  late BuildContext _context;

  /// 임시저장 데이터 check
  Future<void> checkTempData(BuildContext context) async {
    try {
      dynamic response = await LocalDataSource.getLocalData(meatModel.userId!);
      if (response == null) {
        throw Error();
      } else {
        _context = context;
        await _showTempDataDialog(response);
      }
    } catch (e) {
      // TODO : 임시저장 에러 메시지
      debugPrint('Error: $e');
    }
  }

  /// 임시저장 dialog : 임시 데이터 존재시 결정하는 팝업 생성
  Future<void> _showTempDataDialog(dynamic response) async {
    showDataRegisterDialog(
      _context,
      () async {
        // 처음부터 등록
        await LocalDataSource.deleteLocalData(meatModel.userId!);
        notifyListeners();
        if (_context.mounted) _context.pop();
      },
      () async {
        // 이어서 등록
        meatModel.fromJsonTemp(response);
        notifyListeners();
        _context.pop();
      },
    );
  }

  /// STEP 1 : 육류 기본정보 등록
  void clickedBasic(BuildContext context) {
    context.go('/home/registration/trace-num');
  }

  /// STEP 2 : 육류 단면 촬영
  void clickedImage(BuildContext context) {
    if (meatModel.basicCompleted) context.go('/home/registration/image');
  }

  /// STEP 3 : 원육 관능평가
  void clickedFreshmeat(BuildContext context) {
    if (meatModel.imageCompleted) context.go('/home/registration/freshmeat');
  }

  /// 모든 데이터 입력이 완료됐는지 확인하는 함수
  bool checkAllCompleted() {
    return meatModel.basicCompleted &&
        meatModel.imageCompleted &&
        meatModel.sensoryCompleted;
  }

  /// 관리번호 생성 버튼
  void clickCreateBtn(BuildContext context) async {
    // 임시저장된 데이터 삭제
    await LocalDataSource.deleteLocalData(meatModel.userId!);
    // 페이지 이동
    if (context.mounted) context.go('/home/success-registration');
  }

  /// 임시저장 버튼
  Future<void> clickedTempSaveButton(BuildContext context) async {
    try {
      dynamic response = await LocalDataSource.saveDataToLocal(
          meatModel.toJsonTemp(), meatModel.userId!);
      if (response == null) throw Error();
      if (context.mounted) showTemporarySavePopup(context);
    } catch (e) {
      // TODO : 임시저장 에러 메시지 팝업
      debugPrint('Error: $e');
    }
  }
}

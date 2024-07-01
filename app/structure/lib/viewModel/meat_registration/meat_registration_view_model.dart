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

  // 임시저장 데이터 check
  Future<void> checkTempData(BuildContext context) async {
    try {
      dynamic response = await LocalDataSource.getLocalData(meatModel.userId!);
      if (response == null) {
        Error();
      } else {
        _context = context;
        await _showTempDataDialog(response);
        notifyListeners();
      }
    } catch (e) {
      print('에러발생: $e');
    }
  }

  // 임시저장 dialog : 임시 데이터 존재시 결정
  Future<void> _showTempDataDialog(dynamic response) async {
    showDataRegisterDialog(_context, () async {
      // 처음부터 등록
      await LocalDataSource.deleteLocalData(meatModel.userId!);
      popDialog();
    }, () async {
      // 이어서 등록
      isLoading = true;
      notifyListeners();
      meatModel.fromJsonTemp(response);
      isLoading = false;
      notifyListeners();
      popDialog();
    });
  }

  void popDialog() {
    _context.pop();
  }

  // STEP 1 : 육류 기본정보 등록
  void clickedBasic(BuildContext context) {
    context.go('/home/registration/trace-num');
  }

  // STEP 2 : 육류 단면 촬영
  void clickedImage(BuildContext context) {
    context.go('/home/registration/image');
  }

  // STEP 3 : 신선육 관능평가
  void clickedFreshmeat(BuildContext context) {
    context.go('/home/registration/freshmeat');
  }

  // 임시저장 버튼
  Future<void> clickedTempSaveButton(BuildContext context) async {
    isLoading = true;
    notifyListeners();
    try {
      dynamic response = await LocalDataSource.saveDataToLocal(
          meatModel.toJsonTemp(), meatModel.userId!);
      if (response == null) Error();
      isLoading = false;
      notifyListeners();
      _context = context;
      _showTempSavePopup();
    } catch (e) {
      print('에러발생: $e');
    }
    isLoading = false;
    notifyListeners();
  }

  // 임시저장 완료
  void _showTempSavePopup() {
    showTemporarySavePopup(_context);
  }

  // 관리번호 생성 버튼
  void clickedSaveButton(BuildContext context) {
    if (userModel.type == 'Normal') {
      context.go('/home/success-registration-normal');
    } else if (userModel.type == 'Researcher' || userModel.type == 'Manager') {
      context.go('/home/success-registration-researcher');
    } else {
      showUserTypeErrorPopup(context);
    }
  }
}

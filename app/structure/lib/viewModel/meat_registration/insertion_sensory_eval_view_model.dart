//
//
// 관능평가 viewModel.
//
//

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:structure/components/custom_dialog.dart';
import 'package:structure/components/custom_pop_up.dart';
import 'package:structure/dataSource/remote_data_source.dart';
import 'package:structure/model/meat_model.dart';
import 'package:structure/dataSource/local_data_source.dart';
import 'package:structure/model/user_model.dart';

class InsertionSensoryEvalViewModel with ChangeNotifier {
  final MeatModel meatModel;
  final UserModel userModel;
  final BuildContext context;
  InsertionSensoryEvalViewModel(this.meatModel, this.userModel, this.context) {
    _initialize();
  }
  bool isLoading = false;

  // 초기 변수
  String title = '';
  String? meatImage = '';

  // 관능평가 값
  // 초기 값은 1(최하)로 설정
  double marbling = 1;
  double color = 1;
  double texture = 1;
  double surfaceMoisture = 1;
  double overall = 1;

  // 데이터가 존재하면 할당
  void _initialize() {
    if (meatModel.seqno == 0) {
      // 원육
      title = '원육 관능평가';
    } else {
      // 처리육
      title = '처리육 관능평가';
    }

    if (meatModel.sensoryEval != null) {
      meatImage = meatModel.sensoryEval!['imagePath'];
      // 수정 시 불러온 데이터, 등록 시 초기 값 1로 설정
      marbling = meatModel.sensoryEval?["marbling"] ?? 1;
      color = meatModel.sensoryEval?["color"] ?? 1;
      texture = meatModel.sensoryEval?['texture'] ?? 1;
      surfaceMoisture = meatModel.sensoryEval?['surfaceMoisture'] ?? 1;
      overall = meatModel.sensoryEval?['overall'] ?? 1;
    }

    notifyListeners();
  }

  /// 저장 버튼 텍스트
  String saveBtnText() {
    if (meatModel.meatId != null) {
      // 수정 데이터의 경우 수정으로 표시
      return '수정사항 저장';
    } else {
      return '완료';
    }
  }

  /// 뒤로가기 버튼
  VoidCallback? backBtnPressed() {
    return () => showExitDialog(context);
  }

  /// 관능평가 마블링 데이터 할당
  void onChangedMarbling(double value) {
    marbling = double.parse(value.toStringAsFixed(1));
    notifyListeners();
  }

  /// 관능평가 육색 데이터 할당
  void onChangedColor(double value) {
    color = double.parse(value.toStringAsFixed(1));
    notifyListeners();
  }

  /// 관능평가 조직감 데이터 할당
  void onChangedTexture(double value) {
    texture = double.parse(value.toStringAsFixed(1));
    notifyListeners();
  }

  /// 관능평가 육즙 데이터 할당
  void onChangedSurface(double value) {
    surfaceMoisture = double.parse(value.toStringAsFixed(1));
    notifyListeners();
  }

  /// 관능평가 기호도 데이터 할당
  void onChangedOverall(double value) {
    overall = double.parse(value.toStringAsFixed(1));
    notifyListeners();
  }

  // 데이터를 객체에 할당
  Future<void> saveMeatData() async {
    isLoading = true;
    notifyListeners();

    // 처리육의 경우 sensoryEval이 없으면 post 처리
    bool isPost = false;

    if (meatModel.sensoryEval == null && meatModel.seqno != 0) {
      isPost = true;

      meatModel.sensoryEval = {}; // 처리육 관능평가 없으면 생성
      meatModel.sensoryEval!['meatId'] = meatModel.meatId;
      meatModel.sensoryEval!['userId'] = userModel.userId;
      meatModel.sensoryEval!['seqno'] = meatModel.seqno;
    }

    // 관능평가 데이터 입력
    if (meatModel.meatId != null) {
      // 원육 등록이 아닌 경우에는 imgAdded를 false로 처리해야 함
      // 원육 등록의 경우에는 imgAdded = true로 설정돼있음
      meatModel.imgAdded = false;
    }
    meatModel.sensoryEval!['marbling'] = marbling;
    meatModel.sensoryEval!['color'] = color;
    meatModel.sensoryEval!['texture'] = texture;
    meatModel.sensoryEval!['surfaceMoisture'] = surfaceMoisture;
    meatModel.sensoryEval!['overall'] = overall;

    meatModel.checkCompleted();

    // API 전송은 원육 등록이 아닌 경우에만 (meatId != null)
    // 원육은 creation_management_num에서 처리
    if (meatModel.meatId != null) {
      try {
        dynamic response;

        if (isPost) {
          // 처리육 등록
          response = await RemoteDataSource.createMeatData(
              'sensory-eval', meatModel.toJsonSensory());
        } else {
          // 원육/처리육 수정
          response = await RemoteDataSource.patchMeatData(
              'sensory-eval', meatModel.toJsonSensory());
        }

        if (response == 200) {
          meatModel.updateSeonsory();
        } else {
          throw ErrorDescription(response);
        }
      } catch (e) {
        isLoading = false;
        notifyListeners();

        debugPrint('Error: $e');
        if (context.mounted) showErrorPopup(context, error: e.toString());
      }
    } else {
      await tempSave(); // 임시저장
    }

    isLoading = false;
    notifyListeners();

    _goNext();
  }

  void _goNext() {
    if (meatModel.meatId == null) {
      // 신규 등록
      context.go('/home/registration');
    } else {
      // 원육 수정
      if (meatModel.sensoryEval!['seqno'] == 0) {
        showDataManageSucceedPopup(context, () {
          context.go('/home/data-manage-normal/edit');
        });
      } else {
        // 처리육 수정
        context.pop();
      }
    }
  }

  /// 임시저장 버튼
  Future<void> tempSave() async {
    try {
      dynamic response = await LocalDataSource.saveDataToLocal(
          meatModel.toJsonTemp(), meatModel.userId!);
      if (response == null) throw Error();
    } catch (e) {
      debugPrint('Error: $e');
      // TODO : 임시저장 에러 메시지 팝업
    }
  }
}

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

class InsertionSensoryEvalViewModel with ChangeNotifier {
  MeatModel meatModel;

  InsertionSensoryEvalViewModel(this.meatModel) {
    _initialize();
  }
  bool isLoading = false;
  late BuildContext _context;

  // 초기 변수
  String title = '';
  String meatImage = '';

  // 관능평가 값
  // 초기 값은 1(최하)로 설정
  double marbling = 1;
  double color = 1;
  double texture = 1;
  double surfaceMoisture = 1;
  double overall = 1;

  // 데이터가 존재하면 할당
  void _initialize() {
    if (meatModel.sensoryEval != null && meatModel.sensoryEval!['seqno'] == 0) {
      // 원육
      title = '원육 관능평가';
      meatImage = meatModel.sensoryEval!['imagePath'];
      // 수정 시 불러온 데이터, 등록 시 초기 값 1로 설정
      marbling = meatModel.sensoryEval?["marbling"] ?? 1;
      color = meatModel.sensoryEval?["color"] ?? 1;
      texture = meatModel.sensoryEval?['texture'] ?? 1;
      surfaceMoisture = meatModel.sensoryEval?['surfaceMoisture'] ?? 1;
      overall = meatModel.sensoryEval?['overall'] ?? 1;
    }

    // if (meatModel.seqno == 0) {
    //   // 원육
    //   title = '원육 관능평가';
    //   meatImage = meatModel.imagePath!;
    //   marbling = meatModel.freshmeat?["marbling"] ?? 0;
    //   color = meatModel.freshmeat?["color"] ?? 0;
    //   texture = meatModel.freshmeat?['texture'] ?? 0;
    //   surface = meatModel.freshmeat?['surfaceMoisture'] ?? 0;
    //   overall = meatModel.freshmeat?['overall'] ?? 0;
    // } else {
    //   // 처리육
    //   title = '처리육 관능평가';
    //   meatImage = meatModel.deepAgedImage!;
    //   marbling = meatModel.deepAgedFreshmeat?["marbling"] ?? 0;
    //   color = meatModel.deepAgedFreshmeat?["color"] ?? 0;
    //   texture = meatModel.deepAgedFreshmeat?['texture'] ?? 0;
    //   surface = meatModel.deepAgedFreshmeat?['surfaceMoisture'] ?? 0;
    //   overall = meatModel.deepAgedFreshmeat?['overall'] ?? 0;
    // }

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
  VoidCallback? backBtnPressed(BuildContext context) {
    return () => showExitDialog(context);
  }

  /// 관능평가 마블링 데이터 할당
  void onChangedMarbling(double value) {
    marbling = double.parse(value.toStringAsFixed(1));
    // _checkCompleted();
    notifyListeners();
  }

  /// 관능평가 육색 데이터 할당
  void onChangedColor(double value) {
    color = double.parse(value.toStringAsFixed(1));
    // _checkCompleted();
    notifyListeners();
  }

  /// 관능평가 조직감 데이터 할당
  void onChangedTexture(double value) {
    texture = double.parse(value.toStringAsFixed(1));
    // _checkCompleted();
    notifyListeners();
  }

  /// 관능평가 육즙 데이터 할당
  void onChangedSurface(double value) {
    surfaceMoisture = double.parse(value.toStringAsFixed(1));
    // _checkCompleted();
    notifyListeners();
  }

  /// 관능평가 기호도 데이터 할당
  void onChangedOverall(double value) {
    overall = double.parse(value.toStringAsFixed(1));
    // _checkCompleted();
    notifyListeners();
  }

  // 데이터를 객체에 할당
  Future<void> saveMeatData(BuildContext context) async {
    isLoading = true;
    notifyListeners();

    try {
      if (meatModel.sensoryEval != null &&
          meatModel.sensoryEval!['seqno'] == 0) {
        // 원육 등록
        meatModel.sensoryEval!['marbling'] = marbling;
        meatModel.sensoryEval!['color'] = color;
        meatModel.sensoryEval!['texture'] = texture;
        meatModel.sensoryEval!['surfaceMoisture'] = surfaceMoisture;
        meatModel.sensoryEval!['overall'] = overall;

        // 원육 수정
        if (meatModel.meatId != null) {
          meatModel.imgAdded = false;
          final response = await RemoteDataSource.patchMeatData(
              'sensory-eval', meatModel.toJsonSensory());

          if (response != 200) throw Error();
        }
      }

      // if (meatModel.seqno == 0) {
      //   // 원육 - 등록
      //   meatModel.freshmeat ??= {};
      //   meatModel.freshmeat!['createdAt'] = Usefuls.getCurrentDate();
      //   meatModel.freshmeat!['period'] = Usefuls.getMeatPeriod(meatModel);
      //   meatModel.freshmeat!['marbling'] = marbling;
      //   meatModel.freshmeat!['color'] = color;
      //   meatModel.freshmeat!['texture'] = texture;
      //   meatModel.freshmeat!['surfaceMoisture'] = surfaceMoisture;
      //   meatModel.freshmeat!['overall'] = overall;

      //   // 수정
      //   if (meatModel.meatId != null) {
      //     await RemoteDataSource.createMeatData(
      //         'sensory-eval', meatModel.toJsonFresh());
      //   }
      // } else {
      //   // 처리육
      //   meatModel.deepAgedFreshmeat ??= {};
      //   meatModel.deepAgedFreshmeat!['createdAt'] = Usefuls.getCurrentDate();
      //   meatModel.deepAgedFreshmeat!['period'] =
      //       Usefuls.getMeatPeriod(meatModel);
      //   meatModel.deepAgedFreshmeat!['marbling'] = marbling;
      //   meatModel.deepAgedFreshmeat!['color'] = color;
      //   meatModel.deepAgedFreshmeat!['texture'] = texture;
      //   meatModel.deepAgedFreshmeat!['surfaceMoisture'] = surfaceMoisture;
      //   meatModel.deepAgedFreshmeat!['overall'] = overall;

      //   await RemoteDataSource.createMeatData(
      //       'sensory-eval', meatModel.toJsonFresh());
      // }

      meatModel.checkCompleted();
      await tempSave(); // 임시저장

      isLoading = false;
      notifyListeners();

      _context = context;
      _goNext();
    } catch (e) {
      debugPrint('에러발생: $e');
    }
  }

  void _goNext() {
    if (meatModel.meatId == null) {
      // 신규 등록
      _context.go('/home/registration');
    } else {
      // 원육 수정
      if (meatModel.sensoryEval!['seqno'] == 0) {
        showDataManageSucceedPopup(_context, () {
          _context.go('/home/data-manage-normal/edit');
        });
      } else {
        // 처리육 수정
        _context.go('/home/data-manage-researcher/add/processed-meat');
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
    }
  }
}

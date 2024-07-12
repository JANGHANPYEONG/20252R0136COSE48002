//
//
// 신선육 관능평가 viewModel.
//
//

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:structure/components/custom_dialog.dart';
import 'package:structure/components/custom_pop_up.dart';
import 'package:structure/config/userfuls.dart';
import 'package:structure/dataSource/remote_data_source.dart';
import 'package:structure/model/meat_model.dart';
import 'package:structure/dataSource/local_data_source.dart';

class FreshMeatEvalViewModel with ChangeNotifier {
  MeatModel meatModel;

  FreshMeatEvalViewModel(this.meatModel) {
    _initialize();
  }
  // 초기 변수
  String title = '';
  String meatImage = '';

  double marbling = 0;
  double color = 0;
  double texture = 0;
  double surface = 0;
  double overall = 0;

  bool completed = false;
  bool isLoading = false;

  // 데이터가 존재하면 할당
  void _initialize() {
    print(meatModel);
    if (meatModel.seqno == 0) {
      // 원육
      title = '원육 관능평가';
      meatImage = meatModel.imagePath!;
      marbling = meatModel.freshmeat?["marbling"] ?? 0;
      color = meatModel.freshmeat?["color"] ?? 0;
      texture = meatModel.freshmeat?['texture'] ?? 0;
      surface = meatModel.freshmeat?['surfaceMoisture'] ?? 0;
      overall = meatModel.freshmeat?['overall'] ?? 0;
    } else {
      // 처리육
      title = '처리육 관능평가';
      meatImage = meatModel.deepAgedImage!;
      marbling = meatModel.deepAgedFreshmeat?["marbling"] ?? 0;
      color = meatModel.deepAgedFreshmeat?["color"] ?? 0;
      texture = meatModel.deepAgedFreshmeat?['texture'] ?? 0;
      surface = meatModel.deepAgedFreshmeat?['surfaceMoisture'] ?? 0;
      overall = meatModel.deepAgedFreshmeat?['overall'] ?? 0;
    }

    // 완료 체크
    if (marbling != 0 &&
        color != 0 &&
        texture != 0 &&
        surface != 0 &&
        overall != 0) {
      completed = true;
    }
    notifyListeners();
  }

  /// 저장 버튼 텍스트
  String saveBtnText() {
    if (meatModel.seqno == 0) {
      // 원육
      return meatModel.id != null ? '수정사항 저장' : '완료';
    } else {
      return '저장';
    }
  }

  /// 뒤로가기 버튼
  VoidCallback? backBtnPressed(BuildContext context) {
    return () => showExitDialog(context);
  }

  // 관능평가 데이터 값 할당
  void onChangedMarbling(double value) {
    marbling = double.parse(value.toStringAsFixed(1));
    _checkCompleted();
    notifyListeners();
  }

  void onChangedColor(double value) {
    color = double.parse(value.toStringAsFixed(1));
    _checkCompleted();
    notifyListeners();
  }

  void onChangedTexture(double value) {
    texture = double.parse(value.toStringAsFixed(1));
    _checkCompleted();
    notifyListeners();
  }

  void onChangedSurface(double value) {
    surface = double.parse(value.toStringAsFixed(1));
    _checkCompleted();
    notifyListeners();
  }

  void onChangedOverall(double value) {
    overall = double.parse(value.toStringAsFixed(1));
    _checkCompleted();
    notifyListeners();
  }

  // 완료 체크
  void _checkCompleted() {
    if (marbling > 0 &&
        color > 0 &&
        texture > 0 &&
        surface > 0 &&
        overall > 0) {
      completed = true;
    } else {
      completed = false;
    }
  }

  late BuildContext _context;

  // 데이터를 객체에 할당
  Future<void> saveMeatData(BuildContext context) async {
    isLoading = true;
    notifyListeners();

    // 임시저장
    await tempSave(context);

    try {
      if (meatModel.seqno == 0) {
        // 원육 - 등록
        meatModel.freshmeat ??= {};
        meatModel.freshmeat!['createdAt'] = Usefuls.getCurrentDate();
        meatModel.freshmeat!['period'] = Usefuls.getMeatPeriod(meatModel);
        meatModel.freshmeat!['marbling'] = marbling;
        meatModel.freshmeat!['color'] = color;
        meatModel.freshmeat!['texture'] = texture;
        meatModel.freshmeat!['surfaceMoisture'] = surface;
        meatModel.freshmeat!['overall'] = overall;

        // 수정
        if (meatModel.id != null) {
          await RemoteDataSource.sendMeatData(
              'sensory-eval', meatModel.toJsonFresh());
        }
      } else {
        // 처리육
        meatModel.deepAgedFreshmeat ??= {};
        meatModel.deepAgedFreshmeat!['createdAt'] = Usefuls.getCurrentDate();
        meatModel.deepAgedFreshmeat!['period'] =
            Usefuls.getMeatPeriod(meatModel);
        meatModel.deepAgedFreshmeat!['marbling'] = marbling;
        meatModel.deepAgedFreshmeat!['color'] = color;
        meatModel.deepAgedFreshmeat!['texture'] = texture;
        meatModel.deepAgedFreshmeat!['surfaceMoisture'] = surface;
        meatModel.deepAgedFreshmeat!['overall'] = overall;

        await RemoteDataSource.sendMeatData(
            'sensory-eval', meatModel.toJsonFresh());
      }
      meatModel.checkCompleted();
      isLoading = false;
      notifyListeners();
      _goNext();
    } catch (e) {
      print('에러발생: $e');
    }
  }

  void _goNext() {
    if (meatModel.seqno == 0) {
      // 원육
      if (meatModel.id == null) {
        // 등록
        _context.go('/home/registration');
      } else {
        // 수정
        showDataManageSucceedPopup(_context, () {
          _context.go('/home/data-manage-normal/edit');
        });
      }
    } else {
      // 처리육
      _context.go('/home/data-manage-researcher/add/processed-meat');
    }
  }

  /// 임시저장 버튼
  Future<void> tempSave(BuildContext context) async {
    try {
      dynamic response = await LocalDataSource.saveDataToLocal(
          meatModel.toJsonTemp(), meatModel.userId!);
      if (response == null) Error();
      _context = context;
    } catch (e) {
      print('에러발생: $e');
    }
  }
}

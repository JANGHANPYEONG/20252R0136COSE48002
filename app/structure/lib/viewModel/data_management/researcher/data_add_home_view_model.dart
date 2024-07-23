//
//
// 데이터 추가 페이지 (ViewModel) : Researcher
//
//

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import 'package:structure/dataSource/remote_data_source.dart';
import 'package:structure/model/meat_model.dart';
import 'package:structure/screen/data_management/researcher/add_deep_aging_data_screen.dart';
import 'package:structure/viewModel/data_management/researcher/add_deep_aging_data_view_model.dart';

class DataAddHomeViewModel with ChangeNotifier {
  MeatModel meatModel;
  DataAddHomeViewModel(this.meatModel) {
    _initialize();
  }

  bool isLoading = false;

  // 필드 값 표현 변수
  String userName = '-';
  String butcheryDate = '-';
  String speciesValue = '-';
  String secondary = '-';
  String total = '-';

  /// 초기 값 할당 (육류 정보 데이터)
  void _initialize() async {
    userName = meatModel.userName ?? '-';
    butcheryDate = meatModel.butcheryYmd ?? '-';
    speciesValue = meatModel.speciesValue ?? '-';
    secondary = meatModel.secondaryValue ?? '-';

    _setTotal();

    notifyListeners();
  }

  /// 딥에이징 총 횟수, 시간 결산
  void _setTotal() {
    int totalMinutes = meatModel.deepAgingInfo != null
        ? meatModel.deepAgingInfo!
            .map((item) => item['minute'] as int?)
            .where((minute) => minute != null)
            .fold(0, (sum, minute) => sum + (minute ?? 0))
        : 0;

    total = '${meatModel.deepAgingInfo?.length ?? 0}회 / $totalMinutes분';
  }

  // 딥에이징 데이터 삭제
  Future<void> deleteList(int idx) async {
    isLoading = true;
    notifyListeners();

    try {
      int deepAgeIdx = int.parse(
          meatModel.deepAgingData![idx]["deepAgingNum"].split('회')[0]);
      dynamic response =
          await RemoteDataSource.deleteDeepAging(meatModel.meatId!, deepAgeIdx);
      if (response == null) {
        throw Error();
      } else {
        meatModel.deepAgingData!.removeAt(idx);
      }
    } catch (e) {
      debugPrint("Error: $e");
    }

    _setTotal();

    isLoading = false;
    notifyListeners();
  }

  /// 딥 에이징 데이터 추가
  ///
  /// AddDeepAgingDataScreen 호출 후 DB에 딥에이징 추가
  void addDeepAgingData(BuildContext context) {
    isLoading = true;
    notifyListeners();

    // 위젯을 누를 때, 아래 기능이 작동 : 페이지 이동
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ChangeNotifierProvider(
          create: (context) => AddDeepAgingDataViewModel(meatModel: meatModel),
          child: const AddDeepAgingDataScreen(),
        ),
      ),
    ).then((value) async {
      try {
        // 딥에이징 데이터 추가 후 육류 정보 다시 가져오기
        final response = await RemoteDataSource.getMeatData(meatModel.meatId!);
        if (response == 200) {
          _setTotal();
          meatModel.fromJson(response);
        } else {
          throw Error();
        }
      } catch (e) {
        debugPrint('Error: $e');
      }

      isLoading = false;
      notifyListeners();
    });
  }

  /// 원육 데이터 입력 카드 클릭
  Future<void> clickedRawMeat(BuildContext context) async {
    meatModel.fromJsonDeepAged(0); // 원육 정보 가져오기
    if (context.mounted) {
      context.go('/home/data-manage-researcher/add/raw-meat');
    }
  }

  /// 처리육 데이터 입력 카드 클릭
  Future<void> clickedProcessedMeat(int idx, BuildContext context) async {
    // 선택된 회차에 해당하는 딥에이징 데이터 가져오기
    // List builder에서 idx + 1을 한 값을 받아옴
    meatModel.fromJsonDeepAged(idx);

    context.go('/home/data-manage-researcher/add/processed-meat');
  }
}

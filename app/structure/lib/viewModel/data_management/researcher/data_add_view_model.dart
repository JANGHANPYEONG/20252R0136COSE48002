//
//
// 데이터 추가 페이지 (ViewModel) : Researcher
//
//

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_pop_up.dart';
import 'package:structure/dataSource/remote_data_source.dart';
import 'package:structure/model/meat_model.dart';
import 'package:structure/screen/data_management/researcher/add_deep_aging_data_screen.dart';
import 'package:structure/viewModel/data_management/researcher/add_deep_aging_data_view_model.dart';

class DataAddViewModel with ChangeNotifier {
  MeatModel meatModel;
  BuildContext context;
  DataAddViewModel(this.meatModel, this.context) {
    _initialize();
  }

  bool isLoading = false;

  // 필드 값 표현 변수
  String userName = '-';
  String butcheryDate = '-';
  String speciesValue = '-';
  String secondary = '-';
  String total = '-';

  //스크롤바
  final scrollController = ScrollController();

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

    total =
        '${meatModel.deepAgingInfo?.sublist(1).length ?? 0}회 / $totalMinutes분';
  }

  // 딥에이징 데이터 삭제
  Future<void> deleteList(int idx) async {
    isLoading = true;
    notifyListeners();

    try {
      final seqno = int.parse('${meatModel.deepAgingInfo![idx]['seqno']}');

      final response =
          await RemoteDataSource.deleteDeepAging(meatModel.meatId!, seqno);

      if (response != 200) {
        meatModel.deepAgingInfo!.removeAt(idx);
      } else {
        // TODO : 오류 메시지 팝업
        throw ErrorDescription(response);
      }
    } catch (e) {
      debugPrint("Error: $e");
      if (context.mounted) showErrorPopup(context, error: e.toString());
    }

    _setTotal();

    isLoading = false;
    notifyListeners();
  }

  /// 딥 에이징 데이터 추가
  ///
  /// AddDeepAgingDataScreen 호출 후 DB에 딥에이징 추가
  void addDeepAgingData() {
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
      _setTotal();
      notifyListeners();
    });

    isLoading = false;
    notifyListeners();
  }

  /// 원육 데이터 입력 카드 클릭
  Future<void> clickedRawMeat() async {
    meatModel.fromJsonDeepAged(0); // 원육 정보 가져오기

    await GoRouter.of(context)
        .push('/home/data-manage-researcher/add/raw-meat')
        .then((_) => notifyListeners());
  }

  /// 처리육 데이터 입력 카드 클릭
  Future<void> clickedProcessedMeat(int idx) async {
    // 선택된 회차에 해당하는 딥에이징 데이터 가져오기
    // List builder에서 idx + 1을 한 값을 받아옴
    meatModel.fromJsonDeepAged(idx);

    await GoRouter.of(context)
        .push('/home/data-manage-researcher/add/processed-meat')
        .then((_) => notifyListeners());
  }

  /// QR 프린트 버튼 클릭
  void clickedQRButton() {
    context.go('/home/data-manage-researcher/add/qr');
  }
}

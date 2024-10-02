//
//
// 딥에이징 데이터(ViewModel) : Researcher
//
//

import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:structure/components/custom_pop_up.dart';
import 'package:structure/config/usefuls.dart';
import 'package:structure/dataSource/remote_data_source.dart';
import 'package:structure/model/meat_model.dart';

class AddDeepAgingDataViewModel with ChangeNotifier {
  MeatModel meatModel = MeatModel();
  BuildContext context;
  AddDeepAgingDataViewModel({required this.meatModel, required this.context});

  bool isLoading = false;

  // 초음파 처리 시간 컨트롤러
  final TextEditingController textEditingController = TextEditingController();

  // 대상 값들이 입력되었는지 확인 (분, 날짜)
  bool isSelectedDate = false;
  bool isInsertedMinute = false;

  // 날짜 관련 변수
  DateTime selected = DateTime.now(); // 달력에서 선택한 날짜
  DateTime focused = DateTime.now(); // 달력에서 선택한 날짜
  String selectedDate =
      Usefuls.parseDate(Usefuls.getCurrentDate()); // inkwell에 표시할 날짜 string

  // 초음파 처리 시간
  String? selectedMinute;

  /// 입력 상태를 결정짓는다. (날짜, 시간 입력이 완료 되었는지를 체크한다.)
  ///
  /// (state == '선택' : 날짜 입력 | state == value : 시간 입력)
  void changeState(String state) {
    if (state == '선택' && isSelectedDate == false) {
      isSelectedDate = true;
    } else if (state == '선택' && isSelectedDate == true) {
      isSelectedDate = false;
    } else if (int.parse(state) != 0) {
      selectedMinute = state;
      isInsertedMinute = true;
    } else {
      isInsertedMinute = false;
    }

    notifyListeners();
  }

  /// 달력 위젯에서 날짜가 선택될 때 작동
  void onDaySelected(DateTime selectedDays, DateTime focusedDay) {
    selected = selectedDays;
    selectedDate = Usefuls.parseDate(Usefuls.dateTimeToDateString(selected));

    notifyListeners();
  }

  // 데이터 저장
  Future<void> saveData() async {
    isLoading = true;
    notifyListeners();

    int seqno = 1; // Defualt: 첫 딥에이징 seqno (1)

    if (meatModel.deepAgingInfo != null) {
      // 이전 처리육 딥에이징 데이터가 있을 때
      seqno = int.parse('${meatModel.deepAgingInfo!.last['seqno']}') + 1;
    }

    // 전송할 deepAgingInfo json 생성
    String jsonData = jsonEncode({
      'meatId': meatModel.meatId,
      'seqno': seqno,
      'deepAging': {
        'date': Usefuls.dateTimeToDateString(selected),
        'minute': int.parse(selectedMinute!),
      }
    });

    try {
      final response =
          await RemoteDataSource.createMeatData('deep-aging-data', jsonData);

      if (response == 200) {
        // 딥에이징 추가 성공
        meatModel.updateDeepAgingInfo(jsonDecode(jsonData));

        isLoading = false;
        notifyListeners();

        if (context.mounted) Navigator.pop(context);
      } else {
        throw ErrorDescription(response);
      }
    } catch (e) {
      isLoading = false;
      notifyListeners();

      debugPrint('Error: $e');
      if (context.mounted) showErrorPopup(context, error: e.toString());
    }
  }
}

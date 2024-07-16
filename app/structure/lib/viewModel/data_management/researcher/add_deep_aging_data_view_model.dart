//
//
// 딥에이징 데이터(ViewModel) : Researcher
//
//

import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:structure/config/userfuls.dart';
import 'package:structure/dataSource/remote_data_source.dart';
import 'package:structure/model/meat_model.dart';
import 'package:intl/intl.dart';

class AddDeepAgingDataViewModel with ChangeNotifier {
  MeatModel meatModel = MeatModel();

  AddDeepAgingDataViewModel({required this.meatModel});

  // 컨트롤러
  final TextEditingController textEditingController = TextEditingController();

  // 날짜 입력을 위한 기본 변수
  DateTime selected = DateTime.now();
  DateTime focused = DateTime.now();

  // 대상 값들이 입력되었는지 확인 (분, 날짜)
  bool isInsertedMinute = false;
  bool isSelectedDate = false;

  // 대상 값들이 들어오게 될 변수 (선택된 날짜, 처리 시간)
  String selectedMonth = DateTime.now().month.toString();
  String selectedDay = DateTime.now().day.toString();
  String selectedYear = DateTime.now().year.toString();
  String selectedDate = DateFormat('yyyy-MM-dd').format(DateTime.now());
  String? selectedMinute;

  // 현재 위치를 결정 지음(사용되지 않음.)
  int fieldValue = 0;

  // 입력 상태를 결정짓는다. (날짜, 시간 입력이 완료 되었는지를 체크한다.)
  // (state == '선택' : 날짜 입력 | state == value : 시간 입력)
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

  // 달력 위젯에서 날짜가 선택될 때 작동
  void onDaySelected(DateTime selectedDays, DateTime focusedDay) {
    selected = selectedDays; // 이전 날짜를 기억할 수 있도록 변수 보관
    focused = focusedDay; // 이전 날짜를 기억할 수 있도록 변수 보관
    selectedMonth = selected.month.toString();
    selectedYear = selected.year.toString();
    selectedDay = selected.day.toString();

    setDate();
    notifyListeners();
  }

  // 날짜 값 변환 (10 이하의 날짜면 앞에 0을 붙임 : 1일 -> 01일)
  void setDate() {
    if (int.parse(selectedMonth) < 10) {
      selectedMonth = selectedMonth;
    }
    if (int.parse(selectedDay) < 10) {
      selectedDay = selectedDay;
    }
    selectedDate = '$selectedYear-$selectedMonth-$selectedDay';
  }

  late BuildContext _context;

  // 데이터 저장
  Future<void> saveData(BuildContext context) async {
    setDate();

    int seqno = meatModel.deepAgingData!.length + 1;
    String jsonData = jsonEncode({
      "id": meatModel.id,
      "userId": meatModel.createUser,
      "createdAt": Usefuls.getCurrentDate(),
      "period": 0,
      "seqno": seqno,
      "deepAging": {
        "date": '$selectedYear$selectedMonth$selectedDay',
        "minute": int.parse(selectedMinute!),
      }
    });

    try {
      dynamic response =
          await RemoteDataSource.sendMeatData('deep-aging-data', jsonData);
      if (response == null) {
        throw Error();
      } else if (response == 400) {
        meatModel.deepAgingData!.add({
          "deepAgingNum": '$seqno회',
          "date": '$selectedYear$selectedMonth$selectedDay',
          "minute": int.parse(selectedMinute!),
          "complete": false
        });
        _context = context;
        _movePage();
      }
    } catch (e) {}
  }

  void _movePage() {
    Navigator.pop(_context);
  }
}

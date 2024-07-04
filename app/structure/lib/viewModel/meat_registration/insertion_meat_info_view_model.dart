//
//
// 육류 분류 등록 viewModel.
//
//

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:structure/config/pallete.dart';
import 'package:structure/dataSource/remote_data_source.dart';
import 'package:structure/model/meat_model.dart';

class InsertionMeatInfoViewModel with ChangeNotifier {
  MeatModel meatModel;
  InsertionMeatInfoViewModel(this.meatModel) {
    initialize();
  }

  // 초기 변수
  String speciesValue = '';
  String? primalValue;
  String? secondaryValue;

  // 완료 체크
  bool isSelectedSpecies = false;
  bool isSelectedPrimal = false;
  bool isSelectedSecondary = false;
  bool completed = false;

  bool _speciesCheck = false;

  // 'DropdownButton'에 사용될 데이터 변수
  List<String> largeDiv = [];
  List<String> litteDiv = [];
  Map<String, dynamic>? dataTable;

  // 'Togglebutton'에 사용될 위젯 변수
  List<Widget> speciesValues = [
    Text('소', style: Palette.h4Grey),
    Text('돼지', style: Palette.h4Grey),
  ];

  List<bool> selectedSpecies = List.generate(2, (index) => false);

  bool speciesCheckFunc() {
    if (meatModel.speciesValue != null) {
      if (meatModel.speciesValue! == '한우') {
        _speciesCheck = false;
      } else {
        _speciesCheck = true;
      }
    }
    return _speciesCheck;
  }

  Future<void> initialize() async {
    // 초기 데이터 할당
    if (meatModel.speciesValue != null) {
      if (meatModel.speciesValue! == '한우') {
        speciesValue = '소';
        selectedSpecies[0] = true;
      } else {
        speciesValue = meatModel.speciesValue!;
        selectedSpecies[1] = true;
      }
      isSelectedSpecies = true;
    }
    // data fetch
    if (meatModel.secondaryValue != null) {
      primalValue = meatModel.primalValue;
      secondaryValue = meatModel.secondaryValue;
      isSelectedPrimal = true;
      isSelectedSecondary = true;
      completed = true;
    }

    // 종, 부위를 조회 하여, 데이터 할당
    Map<String, dynamic> data = await RemoteDataSource.getMeatSpecies();
    dataTable = data[speciesValue];

    // 종에 따른 대분류 데이터 할당
    List<String> lDiv = [];

    if (dataTable != null) {
      for (String key in dataTable!.keys) {
        lDiv.add(key);
      }
    }

    largeDiv = lDiv;

    if (isSelectedSecondary) {
      litteDiv = List<String>.from(
          dataTable![primalValue].map((element) => element.toString()));
    }

    notifyListeners();
  }

  // 육류 정보 저장
  void saveMeatData() {
    meatModel.speciesValue = speciesValue;
    meatModel.primalValue = primalValue;
    meatModel.secondaryValue = secondaryValue;
  }

  // 종 분류 지정
  void setSpecies() {
    isSelectedSpecies = true;
    isSelectedPrimal = false;
    isSelectedSecondary = false;
    primalValue = null;
    secondaryValue = null;
    notifyListeners();
  }

  // 대분류 지정
  void setPrimal() {
    isSelectedPrimal = true;
    secondaryValue = null;
    isSelectedSecondary = false;
    litteDiv = List<String>.from(
        dataTable![primalValue].map((element) => element.toString()));
    completed = false;
    notifyListeners();
  }

  // 소분류 지정
  void setSecondary() {
    isSelectedSecondary = true;
    completed = true;
    notifyListeners();
  }

  late BuildContext _context;

  // 저장 버튼 : 객체에 데이터 할당
  Future<void> clickedNextButton(BuildContext context) async {
    saveMeatData();
    meatModel.checkCompleted();
    if (meatModel.id != null) {
      final response =
          await RemoteDataSource.sendMeatData(null, meatModel.toJsonBasic());

      if (response == null) {
        // 에러 페이지
      } else {
        _context = context;
        _movePage();
      }
    } else {
      context.go('/home/registration');
    }
  }

  void _movePage() {
    _context.go('/home/data-manage-normal/edit');
  }
}

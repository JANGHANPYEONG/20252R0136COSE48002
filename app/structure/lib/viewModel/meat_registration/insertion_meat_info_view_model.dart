//
//
// 육류 분류 등록 viewModel.
//
//

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:structure/components/custom_dialog.dart';
import 'package:structure/config/pallete.dart';
import 'package:structure/dataSource/remote_data_source.dart';
import 'package:structure/model/meat_model.dart';
import 'package:structure/dataSource/local_data_source.dart';
import 'package:structure/components/custom_pop_up.dart';

class InsertionMeatInfoViewModel with ChangeNotifier {
  MeatModel meatModel;
  InsertionMeatInfoViewModel(this.meatModel) {
    initialize();
  }
  bool isLoading = false;

  // 초기 변수
  String speciesValue = '';
  String? primalValue;
  String? secondaryValue;

  // 완료 체크
  bool isSelectedSpecies = false; // 종류 선택 완료 여부
  bool isSelectedPrimal = false; // 대분할 선택 완료 여부
  bool isSelectedSecondary = false; // 소분할 선택 완료 여부
  bool completed = false; // 전체 완료 여부

  // 'DropdownButton'에 사용될 데이터 변수
  List<String> largeDiv = [];
  List<String> litteDiv = [];
  Map<String, dynamic>? dataTable;

  // 'Togglebutton'에 사용될 위젯 변수
  List<Widget> speciesValues = [
    Text('소', style: Palette.h4Grey),
    Text('돼지', style: Palette.h4Grey),
  ];

  // 선택된 species
  // 0 - 소, 1 - 돼지
  List<bool> selectedSpecies = List.generate(2, (index) => false);

  /// 초기 데이터 할당
  Future<void> initialize() async {
    if (meatModel.speciesValue != null) {
      // 축산물 api에서 받아온 데이터는 한우가 될 수도 있음
      if (meatModel.speciesValue! == '한우') {
        // 소 설정
        speciesValue = '소';
        selectedSpecies[0] = true;
      } else {
        // 돼지 설정
        speciesValue = meatModel.speciesValue!;
        selectedSpecies[1] = true;
      }

      isSelectedSpecies = true;
    }

    // primaryValue, secondaryValue가 null이 아니면 수정하는 데이터
    // 소분할
    if (meatModel.secondaryValue != null) {
      primalValue = meatModel.primalValue; // 대분할 설정
      secondaryValue = meatModel.secondaryValue; // 소분할 설정
      isSelectedPrimal = true;
      isSelectedSecondary = true;
      completed = true;
    }

    // 종, 부위를 조회 하여, 데이터 할당
    try {
      dynamic response = await RemoteDataSource.getMeatSpecies();
      if (response is Map<String, dynamic>) {
        dataTable = response[speciesValue];
      } else {
        throw Error();
      }
    } catch (e) {
      debugPrint('Error getting getMeatSpecies: $e');
    }

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

  /// 소인지 확인하는 함수
  /// true - 돼지, false - 소
  bool speciesCheckFunc() {
    return speciesValue == '돼지';
  }

  /// 육류 정보 저장
  void saveMeatData() {
    meatModel.speciesValue = speciesValue; // 한우일 수 있기 때문에 업데이트
    meatModel.primalValue = primalValue;
    meatModel.secondaryValue = secondaryValue;
  }

  /// 대분류 지정
  void setPrimal() {
    isSelectedPrimal = true;
    secondaryValue = null;
    isSelectedSecondary = false;
    litteDiv = List<String>.from(
        dataTable![primalValue].map((element) => element.toString()));
    completed = false;
    notifyListeners();
  }

  /// 소분류 지정
  void setSecondary() {
    isSelectedSecondary = true;
    if (isSelectedPrimal) completed = true;
    notifyListeners();
  }

  /// 뒤로가기 버튼
  VoidCallback? backBtnPressed(BuildContext context) {
    return () {
      showExitDialog(context);
    };
  }

  /// 저장 버튼 : 객체에 데이터 할당
  Future<void> clickedNextButton(BuildContext context) async {
    isLoading = true;
    notifyListeners();

    saveMeatData();
    meatModel.checkCompleted();
    await tempSave();

    // meatId가 null이 아니면 수정하는 데이터
    if (meatModel.meatId != null) {
      // TODO: PATCH로 변경
      final response =
          await RemoteDataSource.createMeatData(null, meatModel.toJsonBasic());

      if (response == null) {
        // 에러 페이지
      } else {
        isLoading = false;
        notifyListeners();

        if (context.mounted) {
          showDataManageSucceedPopup(
            context,
            () => context.go('/home/data-manage-normal/edit'),
          );
        }
      }
    } else {
      isLoading = false;
      notifyListeners();
      if (context.mounted) context.go('/home/registration');
    }
  }

  /// 임시저장 버튼
  Future<void> tempSave() async {
    try {
      dynamic response = await LocalDataSource.saveDataToLocal(
          meatModel.toJsonTemp(), meatModel.userId!);
      if (response == null) Error();
    } catch (e) {
      debugPrint('에러발생: $e');
    }
  }
}

//
//
// 육류 이력번호 등록 viewModel.
//
//

import 'dart:async';

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import 'package:structure/dataSource/remote_data_source.dart';
import 'package:structure/model/meat_model.dart';

class InsertionTraceNumViewModel with ChangeNotifier {
  final MeatModel meatModel;
  InsertionTraceNumViewModel(this.meatModel) {
    initialize();
  }

  //table 조회 상태 변수
  bool isTableVisible = false;

  // form key
  final formKey = GlobalKey<FormState>();

  // api key
  var apikey =
      "%2FuEP%2BvIjYfPTyaHNlxRx2Ry5cVUer92wa6lHcxnXEEekVjUCZ1N41traj3s8sGhHpKS54SVDbg9m4sHOEuMNuw%3D%3D";

  // text controller
  final TextEditingController textEditingController = TextEditingController();

  // 데이터를 담는 리스트
  final List<String?> tableData = [];

  // 데이터가 모두 입력 되었는지 확인.
  int isAllInserted = 0;

  // 데이터를 임시로 담을 변수를 지정.
  String? traceNum;
  String? birthYmd;
  String? species;
  String? sexType;
  String? farmerNm;
  String? farmAddr;
  String? butcheryYmd;
  String? gradeNum;

  // 초기 실행 함수
  void initialize() {
    // 데이터가 meatModel에 존재하면 해당 데이터를 할당. (데이터 관리 전용)
    if (meatModel.basicCompleted) {
      traceNum = meatModel.traceNum;
      birthYmd = meatModel.birthYmd;
      species = meatModel.speciesValue;
      sexType = meatModel.sexType;
      farmerNm = meatModel.farmerNm;
      farmAddr = meatModel.farmAddr;
      butcheryYmd = meatModel.butcheryYmd;
      gradeNum = meatModel.gradeNum;
      tableData.addAll([
        traceNum,
        farmerNm,
        farmAddr,
        butcheryYmd,
        species,
        sexType,
        gradeNum,
        birthYmd,
      ]);
      isAllInserted = 1;
    }
  }

  // 바코드 관련 기능을 정의.
  void getBarcodeValue(dynamic event) {
    textEditingController.text = event.toString();
    reset();
    notifyListeners();
  }

  // api를 통해 얻어온 육류의 정보를 meatModel 객체에 저장
  void saveMeatData() {
    if (meatModel.traceNum != null && meatModel.traceNum != traceNum) {
      meatModel.speciesValue = null;
      meatModel.primalValue = null;
      meatModel.secondaryValue = null;
    }
    meatModel.traceNum = traceNum;
    meatModel.farmAddr = farmAddr;
    meatModel.farmerNm = farmerNm;
    meatModel.butcheryYmd = butcheryYmd;
    meatModel.birthYmd = birthYmd;
    meatModel.sexType = sexType;
    meatModel.speciesValue = species;
    meatModel.gradeNum = gradeNum;
  }

  void hideTable() {
    isTableVisible = false;
    // meatModel.traceNum = null;
    notifyListeners();
  }

  void showTable() {
    isTableVisible = true;
    notifyListeners();
  }

  // 새롭게 검색을 누를 때, 기존 데이터 초기화 (육종 별 데이터가 다름)
  void reset() {
    tableData.clear();
    traceNum = null;
    birthYmd = null;
    species = null;
    sexType = null;
    farmerNm = null;
    farmAddr = null;
    butcheryYmd = null;
    gradeNum = null;
    isAllInserted = 0;
  }

  // 텍스트의 유효성 검사를 진행.
  bool tryValidation() {
    final isValid = formKey.currentState!.validate();
    if (isValid) {
      // 유효하면, 현재 form의 값을 전달.
      formKey.currentState!.save();
      return true;
    } else {
      // 유효하지 않으면 form에게 alert를 알리고, 초기화.
      reset();
      return false;
    }
  }

  // 검색 버튼을 눌렀을 때, 관련 작업을 진행.
  void start(BuildContext context) async {
    // 키보드를 내린다.
    FocusScope.of(context).unfocus();

    tableData.clear();
    // validation 검사를 진행.
    bool isValid = tryValidation();

    if (isValid) {
      // 만약 valid하면, api로부터 데이터를 받는다.
      await fetchData(traceNum!);
    }

    // 이후 작업을 위해, text field를 비운다.
    // textEditingController.clear();

    // provider에게 신호를 보낸다.
    notifyListeners();
  }

  void clearText(BuildContext context) async {
    // 이후 작업을 위해, text field를 비운다.
    textEditingController.clear();
  }

  // fetchData
  Future<void> fetchData(String historyNo) async {
    // 모든 공백을 제거한다.
    historyNo = historyNo.replaceAll(RegExp('\\s'), "");

    // 변수와 테이블을 먼저 초기화.
    reset();

    // 만일 묶음 번호가 들어온다면, 처리하여 이력 번호로 갱신. (돼지의 경우)
    if (historyNo.startsWith('L1')) {
      try {
        final pigAPIData = await RemoteDataSource.getMeatTraceData(
            "http://data.ekape.or.kr/openapi-data/service/user/animalTrace/traceNoSearch?serviceKey=$apikey&traceNo=$historyNo&optionNo=9");
        if (pigAPIData == null) throw Error();

        if (pigAPIData['response']['body']['items']['item'][0] == null) {
          traceNum = pigAPIData['response']['body']['items']['item']['pigNo'];
        } else {
          traceNum =
              pigAPIData['response']['body']['items']['item'][0]['pigNo'];
        }
      } catch (e) {
        reset();
        isAllInserted = 2;
      }
    } else {
      // 그렇지 않다면 이력 번호로 취급.
      traceNum = historyNo;
    }

    // 이력 번호의 시작이 '0'인 경우. (소의 경우)
    if (traceNum!.startsWith('0')) {
      try {
        final meatAPIData1 = await RemoteDataSource.getMeatTraceData(
            "http://data.ekape.or.kr/openapi-data/service/user/animalTrace/traceNoSearch?serviceKey=$apikey&traceNo=$traceNum&optionNo=1");
        final meatAPIData2 = await RemoteDataSource.getMeatTraceData(
            "http://data.ekape.or.kr/openapi-data/service/user/animalTrace/traceNoSearch?serviceKey=$apikey&traceNo=$traceNum&optionNo=2");
        final meatAPIData3 = await RemoteDataSource.getMeatTraceData(
            "http://data.ekape.or.kr/openapi-data/service/user/animalTrace/traceNoSearch?serviceKey=$apikey&traceNo=$traceNum&optionNo=3");

        String? date =
            meatAPIData1['response']['body']['items']['item']['birthYmd'] ?? "";
        birthYmd = DateFormat('yyyyMMdd')
            .format(DateTime.parse(date!))
            .toString(); // 날짜 형식을 yyyyMMdd로 변경

        species =
            meatAPIData1['response']['body']['items']['item']['lsTypeNm'] ?? "";
        sexType =
            meatAPIData1['response']['body']['items']['item']['sexNm'] ?? "";

        farmerNm = meatAPIData2['response']['body']['items']['item'][0]
                ['farmerNm'] ??
            "";
        farmAddr = meatAPIData2['response']['body']['items']['item'][0]
                ['farmAddr'] ??
            "";

        String? butDate = meatAPIData3['response']['body']['items']['item']
                ['butcheryYmd'] ??
            "";
        butcheryYmd = DateFormat('yyyyMMdd')
            .format(DateTime.parse(butDate!))
            .toString(); // 날짜 형식을 yyyyMMdd로 변경

        gradeNum =
            meatAPIData3['response']['body']['items']['item']['gradeNm'] ?? "";
      } catch (e) {
        reset();
        isAllInserted = 2;
      }
    } else {
      // 이력 번호의 시작이 '1'인 경우. (돼지의 경우)
      try {
        final meatAPIData4 = await RemoteDataSource.getMeatTraceData(
            "http://data.ekape.or.kr/openapi-data/service/user/animalTrace/traceNoSearch?serviceKey=$apikey&traceNo=$traceNum&optionNo=4");
        final meatAPIData3 = await RemoteDataSource.getMeatTraceData(
            "http://data.ekape.or.kr/openapi-data/service/user/animalTrace/traceNoSearch?serviceKey=$apikey&traceNo=$traceNum&optionNo=3");

        gradeNum = meatAPIData4['response']['body']['items']['item']['gradeNm'];

        String? time = meatAPIData3['response']['body']['items']['item']
                ['butcheryYmd'] ??
            "";
        butcheryYmd = DateFormat('yyyyMMdd')
            .format(DateTime.parse(time!))
            .toString(); // 날짜 형식을 yyyyMMdd로 변경

        species = '돼지';
      } catch (e) {
        reset();
        isAllInserted = 2;
      }
    }
    if (butcheryYmd != null) {
      // 데이터를 table list에 할당.
      tableData.addAll([
        traceNum,
        farmerNm,
        farmAddr,
        butcheryYmd,
        species,
        sexType,
        gradeNum,
        birthYmd,
      ]);
      isAllInserted = 1;
    } else {
      isAllInserted = 2;
    }
  }

  // 다음 버튼을 눌렀을 때 동작.
  void clickedNextbutton(BuildContext context) {
    saveMeatData();
    if (meatModel.id != null) {
      context.go('/home/data-manage-normal/edit/trace-editable/info-editable');
    } else {
      context.go('/home/registration/trace-num/meat-info');
    }
  }
}

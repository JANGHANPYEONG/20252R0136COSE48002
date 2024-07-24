//
//
// 육류 모델
//
//

import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:structure/main.dart';

class MeatModel with ChangeNotifier {
  /* 육류 기본 정보 */
  String? meatId; // 육류 id
  String? createdAt; // 육류 정보 생성 날짜
  // 정보를 등록한 사용자 정보
  String? userId; // 육류를 등록한 사용자 id
  String? userName; // 육류 등록한 사용자 이름
  // 데이터 승인상태
  String? statusType; // 0 - 대기, 1 - 반려, 2 - 승인
  // QR 이미지 경로
  String? imagePath;
  // 육류 부위 정보
  String? primalValue; // 대분할
  String? secondaryValue; // 소분할
  // 육류 오픈 API 데이터
  String? traceNum;
  String? farmerName;
  String? farmAddr;
  String? butcheryYmd;
  String? speciesValue;
  String? sexType;
  String? gradeNum;
  String? birthYmd;

  /* 딥에이징 관련 데이터 */
  /// 딥에이징 데이터
  ///
  /// seqno가 0일 경우 원육, 1 이상일 경우 처리육
  ///
  /// int seqno
  /// <br /> String date
  /// <br /> int minute
  /// <br /> Map<String, dynamic> sensory_eval
  /// <br /> Map<String, dynamic> heated_meat_sensory_eval
  /// <br /> Map<String, dynamic> probexpt_data
  /// <br /> Map<String, dynamic> heatedmeat_probexpt_data
  List<dynamic>? deepAgingInfo;

  /// 선택된 데이터의 seqno
  int? seqno;

  /// 관능평가 데이터
  ///
  /// String meatId
  /// <br /> String userId
  /// <br /> String userName
  /// <br /> String imagePath
  /// <br /> String filmedAt (yyyy-MM-ddThh:mm:ss)
  /// <br /> int seqno
  /// <br /> int period
  /// <br /> Sring createdAt (yyyy-MM-ddThh:mm:ss)
  /// <br /> double marbling
  /// <br /> double color
  /// <br /> double texture
  /// <br /> double surfaceMoisture
  /// <br /> double overall
  Map<String, dynamic>? sensoryEval;
  // 이미지 신규 추가 여부
  bool imgAdded = false;

  /// 가열육 관능평가 데이터
  ///
  /// String meatId
  /// <br /> String userId
  /// <br /> String userName
  /// <br /> String imagePath
  /// <br /> String filmedAt (yyyy-MM-ddThh:mm:ss)
  /// <br /> int seqno
  /// <br /> int period
  /// <br /> String createdAt (yyyy-MM-ddThh:mm:ss)
  /// <br /> double flavor
  /// <br /> double juiciness
  /// <br /> double palatability
  /// <br /> double tenderness
  /// <br /> double umami
  Map<String, dynamic>? heatedSensoryEval;
  // 이미지 신규 추가 여부
  bool heatedImgAdded = false;

  /// 전자혀 + 실험실 데이터
  ///
  /// String meatId
  /// <br /> String userId
  /// <br /> String userName
  /// <br /> int seqno
  /// <br /> int period
  /// <br /> String updatedAt
  /// <br /> double L
  /// <br /> double a
  /// <br /> double b
  /// <br /> double DL
  /// <br /> double CL
  /// <br /> double RW
  /// <br /> double ph
  /// <br /> double WBSF
  /// <br /> double cardepsin_activity
  /// <br /> double MFI
  /// <br /> double Collagen
  /// <br /> double sourness
  /// <br /> double bitterness
  /// <br /> double umami
  /// <br /> double richness
  Map<String, dynamic>? probExpt;

  /// 가열육 전자혀 + 실험실 데이터
  ///
  /// String meatId
  /// <br /> String userId
  /// <br /> String userName
  /// <br /> int seqno
  /// <br /> int period
  /// <br /> String updatedAt
  /// <br /> double L
  /// <br /> double a
  /// <br /> double b
  /// <br /> double DL
  /// <br /> double CL
  /// <br /> double RW
  /// <br /> double ph
  /// <br /> double WBSF
  /// <br /> double cardepsin_activity
  /// <br /> double MFI
  /// <br /> double Collagen
  /// <br /> double sourness
  /// <br /> double bitterness
  /// <br /> double umami
  /// <br /> double richness
  Map<String, dynamic>? heatedProbExpt;

  /* 데이터 입력 완료 확인 */
  /// 육류 기본정보 입력 완료 여부
  ///
  /// traceNum, farmerName, farmAddr,butcheryYmd, speciesValue, sexType, gradeNum, birthYmd, primalValue, secondaryValue
  bool basicCompleted = false;

  /// 원육 이미지 등록 완료 여부
  ///
  /// imagePath
  bool imageCompleted = false;

  /// 원육 관능평가 등록 완료 여부
  ///
  /// marbling, color, texture, surfaceMoisture, overall
  bool sensoryCompleted = false;

  // /// 처리육 이미지 등록 완료 여부
  // ///
  // /// imagePath
  // bool processedImageCompleted = false;

  // /// 처리육 관능평가 등록 완료 여부
  // ///
  // /// marbling, color, texture, surfaceMoisture, overall
  // bool processedSensoryCompleted = false;

  /// 원육/처리육 전자혀 데이터 등록 완료 여부
  ///
  /// sourness, bitterness, umami, richness
  bool tongueCompleted = false;

  /// 원육/처리육 실험 데이터 등록 완료 여부
  ///
  /// L, a, b, DL, CL, RW, ph, WBSF, cardepsin_activity, MFI, Collagen
  bool labCompleted = false;

  /// 가열육 단면 촬영 등록 완료 여부
  ///
  /// imagePath
  bool heatedImageCompleted = false;

  /// 가열육 관능평가 완료 여부
  ///
  /// flavor, juiciness, tenderness, umami, palatability
  bool heatedSensoryCompleted = false;

  /// 가열육 전자혀 데이터 등록 완료 여부
  ///
  /// sourness, bitterness, umami, richness
  bool heatedTongueCompleted = false;

  /// 가열육 실험 데이터 등록 완료 여부
  ///
  /// L, a, b, DL, CL, RW, ph, WBSF, cardepsin_activity, MFI, Collagen
  bool heatedLabCompleted = false;

  // 미완료
  // 육류 이미지 경로
  String? deepAgedImage;

  // 신선육 관능평가 데이터
  Map<String, dynamic>? freshmeat;
  Map<String, dynamic>? deepAgedFreshmeat;

  // 연구 데이터 추가 입력 완료 시 저장
  List<Map<String, dynamic>>? deepAgingData;
  Map<String, dynamic>? heatedmeat;
  Map<String, dynamic>? probexptData;

  Map<String, dynamic>? processedmeat;
  Map<String, dynamic>? rawmeat;

  // 외부 데이터 입력 완료 체크
  bool rawmeatDataComplete = false;
  Map<String, dynamic>? processedmeatDataComplete;
  bool deepAgedImageCompleted = false;
  bool deepAgedFreshCompleted = false;
  bool heatedCompleted = false;

  // Constructor
  // 미완료
  MeatModel({
    // 관리 번호 생성 시 저장
    this.meatId,
    this.userId,
    this.sexType,
    this.gradeNum,
    this.statusType,
    this.createdAt,
    this.traceNum,
    this.farmAddr,
    this.farmerName,
    this.butcheryYmd,
    this.birthYmd,
    this.userName,
    // Species, primal, secondary를 토대로 백에서 categoryId 생성
    this.speciesValue,
    this.primalValue,
    this.secondaryValue,
    this.deepAgedImage,
    this.seqno,
    this.freshmeat,
    this.deepAgedFreshmeat,

    // 연구 데이터 추가 입력 완료 시 저장
    this.deepAgingData,
    this.heatedmeat,
    this.probexptData,

    // 데이터 fetch 시 저장
    this.processedmeat,
    this.rawmeat,

    // // 데이터 입력 완료시 저장
    this.processedmeatDataComplete,
  });

  /// 임시 데이터 저장
  String toJsonTemp() {
    return jsonEncode({
      /* 육류 기본 정보 */
      'traceNum': traceNum,
      'farmerName': farmerName,
      'farmAddr': farmAddr,
      'butcheryYmd': butcheryYmd,
      'specieValue': speciesValue,
      'primalValue': primalValue,
      'secondaryValue': secondaryValue,
      'sexType': sexType,
      'gradeNum': gradeNum,
      'birthYmd': birthYmd,
      /* 딥에이징 데이터 */
      'sensoryEval': sensoryEval,
      'imgAdded': imgAdded,
      /* 완료 여부 */
      'basicCompleted': basicCompleted,
      'rawImageCompleted': imageCompleted,
      'rawSensoryCompleted': sensoryCompleted
    });
  }

  /// 임시 데이터 할당
  void fromJsonTemp(Map<String, dynamic> jsonData) {
    /* 육류 기본 정보 */
    traceNum = jsonData['traceNum'];
    farmerName = jsonData['farmerName'];
    farmAddr = jsonData['farmAddr'];
    butcheryYmd = jsonData['butcheryYmd'];
    speciesValue = jsonData['specieValue'];
    primalValue = jsonData['primalValue'];
    secondaryValue = jsonData['secondaryValue'];
    sexType = jsonData['sexType'];
    gradeNum = jsonData['gradeNum'];
    birthYmd = jsonData['birthYmd'];
    /* 딥에이징 데이터 */
    sensoryEval = jsonData['sensoryEval'];
    imgAdded = jsonData['imgAdded'];
    /* 완료 여부 */
    basicCompleted = jsonData['basicCompleted'];
    imageCompleted = jsonData['rawImageCompleted'];
    sensoryCompleted = jsonData['rawSensoryCompleted'];
  }

  /// 육류 기본 정보 json 변환
  ///
  /// meatId, userId, sexType, gradeNum, specieValue, primalValue, secondaryValue, traceNum, farmAddr, farmerName, butcheryYmd, birthYmd
  String toJsonBasic() {
    return jsonEncode({
      'meatId': meatId,
      'userId': userId,
      'sexType': sexType,
      'gradeNum': gradeNum,
      'specieValue': speciesValue,
      'primalValue': primalValue,
      'secondaryValue': secondaryValue,
      'traceNum': traceNum,
      'farmAddr': farmAddr,
      'farmerName': farmerName,
      'butcheryYmd': butcheryYmd,
      'birthYmd': birthYmd,
    });
  }

  /// 관능평가 데이터 정보 json 변환
  ///
  /// meatId, userId, seqno, imgAdded, filmedAt, marbling, color, texture, surfaceMoisture, overall
  String toJsonSensory() {
    return jsonEncode({
      'meatId': sensoryEval!['meatId'],
      'userId': sensoryEval!['userId'],
      'seqno': sensoryEval!['seqno'],
      'imgAdded': imgAdded,
      'filmedAt': sensoryEval!['filmedAt'],
      'sensoryData': {
        'marbling': sensoryEval!['marbling'],
        'color': sensoryEval!['color'],
        'texture': sensoryEval!['texture'],
        'surfaceMoisture': sensoryEval!['surfaceMoisture'],
        'overall': sensoryEval!['overall'],
      }
    });
  }

  /// 가열육 관능평가 데이터 정보 json 변환
  ///
  /// meatId, userId, seqno, imgAdded, filmedAt, marbling, color, texture, surfaceMoisture, overall
  String toJsonHeatedSensory() {
    return jsonEncode({
      'meatId': heatedSensoryEval!['meatId'],
      'userId': heatedSensoryEval!['userId'],
      'seqno': heatedSensoryEval!['seqno'],
      'imgAdded': heatedImgAdded,
      'filmedAt': heatedSensoryEval!['filmedAt'],
      'heatedmeatSensoryData': {
        'flavor': heatedSensoryEval!['flavor'],
        'juiciness': heatedSensoryEval!['juiciness'],
        'tenderness': heatedSensoryEval!['tenderness'],
        'umami': heatedSensoryEval!['umami'],
        'palatability': heatedSensoryEval!['palatability'],
      }
    });
  }

  /// probExpt 정보 json 변환
  ///
  /// meatId, userId, seqno, isHeated, L, a, b, DL, CL, RW, ph, WBSF, cardepsin_activity, MFI, Collagen, sourness, bitterness, umami, richness
  String toJsonProbExpt() {
    return jsonEncode({
      'meatId': probExpt!['meatId'],
      'userId': probExpt!['userId'],
      'seqno': probExpt!['seqno'],
      'isHeated': false,
      'probexptData': {
        'L': probExpt?['L'],
        'a': probExpt?['a'],
        'b': probExpt?['b'],
        'DL': probExpt?['DL'],
        'CL': probExpt?['CL'],
        'RW': probExpt?['RW'],
        'ph': probExpt?['ph'],
        'WBSF': probExpt?['WBSF'],
        'cardepsin_activity': probExpt?['cardepsin_activity'],
        'MFI': probExpt?['MFI'],
        'Collagen': probExpt?['Collagen'],
        'sourness': probExpt?['sourness'],
        'bitterness': probExpt?['bitterness'],
        'umami': probExpt?['umami'],
        'richness': probExpt?['richness'],
      },
    });
  }

  /// heatedProbExpt 정보 json 변환
  ///
  /// meatId, userId, seqno, isHeated, L, a, b, DL, CL, RW, ph, WBSF, cardepsin_activity, MFI, Collagen, sourness, bitterness, umami, richness
  String toJsonHeatedProbExpt() {
    return jsonEncode({
      'meatId': heatedProbExpt!['meatId'],
      'userId': heatedProbExpt!['userId'],
      'seqno': heatedProbExpt!['seqno'],
      'isHeated': true,
      'probexptData': {
        'L': heatedProbExpt?['L'],
        'a': heatedProbExpt?['a'],
        'b': heatedProbExpt?['b'],
        'DL': heatedProbExpt?['DL'],
        'CL': heatedProbExpt?['CL'],
        'RW': heatedProbExpt?['RW'],
        'ph': heatedProbExpt?['ph'],
        'WBSF': heatedProbExpt?['WBSF'],
        'cardepsin_activity': heatedProbExpt?['cardepsin_activity'],
        'MFI': heatedProbExpt?['MFI'],
        'Collagen': heatedProbExpt?['Collagen'],
        'sourness': heatedProbExpt?['sourness'],
        'bitterness': heatedProbExpt?['bitterness'],
        'umami': heatedProbExpt?['umami'],
        'richness': heatedProbExpt?['richness'],
      },
    });
  }

  /* deepAgingInfo 업데이트 함수 */
  /// 새로 추가된 deepAgingInfo 데이터를 로컬 deepAgingInfo에 추가하는 함수
  /// <br /> DB에 데이터 전송 후 200인 경우에만 실행
  void updateDeepAgingInfo(Map<String, dynamic> jsonData) {
    Map<String, dynamic> info = {
      'date': DateFormat('yyyyMMdd')
          .format(DateTime.parse(jsonData['deepAging']['date'])),
      'minute': jsonData['deepAging']['minute'],
      'seqno': jsonData['seqno'],
      'sensory_eval': null,
      'heated_meat_sensory_eval': null,
      'probexpt_data': null,
      'heatedmeat_probexpt_data': null,
    };

    deepAgingInfo!.add(info);
  }

  /// 새로 추가된 heatedProbExpt 데이터를 로컬 deepAgingInfo에 추가하는 함수
  /// <br /> DB에 데이터 전송 후 200인 경우에만 실행
  void updateHeatedSeonsory() {
    final info = deepAgingInfo!.firstWhere(
        (item) => item['seqno'] == '${heatedSensoryEval!['seqno']}');
    info['heated_meat_sensory_eval'] = heatedSensoryEval;
  }

  /// 새로 추가된 heatedProbExpt 데이터를 로컬 deepAgingInfo에 추가하는 함수
  /// <br /> DB에 데이터 전송 후 200인 경우에만 실행
  void updateProbExpt() {
    final info = deepAgingInfo!
        .firstWhere((item) => item['seqno'] == '${probExpt!['seqno']}');
    info['probexpt_data'] = probExpt;
  }

  /// 새로 추가된 heatedProbExpt 데이터를 로컬 deepAgingInfo에 추가하는 함수
  /// <br /> DB에 데이터 전송 후 200인 경우에만 실행
  void updateHeatedProbExpt() {
    final info = deepAgingInfo!
        .firstWhere((item) => item['seqno'] == '${heatedProbExpt!['seqno']}');
    info['heatedmeat_probexpt_data'] = heatedProbExpt;
  }

  // 미완료

  /// 육류 전체 데이터 저장
  void fromJson(Map<String, dynamic> jsonData) {
    reset(); // 데이터 받아올 때는 항상 초기화 먼저

    // 기본 데이터
    meatId = jsonData['meatId'];
    createdAt = jsonData['createdAt'];
    userId = jsonData['userId'];
    userName = jsonData['userName'];
    statusType = jsonData['statusType'];
    imagePath = jsonData['imagePath'];
    primalValue = jsonData['primalValue'];
    secondaryValue = jsonData['secondaryValue'];
    traceNum = jsonData['traceNum'];
    farmerName = jsonData['farmerName'];
    farmAddr = jsonData['farmAddr'];
    butcheryYmd = jsonData['butcheryYmd'];
    speciesValue = jsonData['specieValue'];
    sexType = jsonData['sexType'];
    gradeNum = jsonData['gradeNum'];
    birthYmd = jsonData['birthYmd'];

    // 딥에이징 데이터
    deepAgingInfo = jsonData['deepAgingInfo'];

    // 아마 이 이후는 지워도 될듯?

    // // sensoryEval = jsonData['deepAgingInfo'];

    // // deepAgedImage = jsonData['deepAgedImage'];

    // freshmeat = jsonData['rawmeat']['sensory_eval'];
    // // deepAgedFreshmeat = jsonData['deepAgedFreshmeat'];

    // // 딥에이징 데이터 입력시 저장
    // // heatedmeat = jsonData['heatedmeat'];
    // // tongueData = jsonData['tongueData'];
    // // labData = jsonData['labData'];

    // // 데이터 fetch 시 저장
    // processedmeat = jsonData['processedmeat'];
    // rawmeat = jsonData['rawmeat'];

    // // 데이터 입력 완료시 저장
    // rawmeatDataComplete = jsonData['rawmeat_data_complete'];
    // // rawmeatDataComplete = jsonData['rawmeat_data_complete'] ? true : false;
    // processedmeatDataComplete = jsonData['processedmeat_data_complete'] == false
    //     ? {}
    //     : jsonData['processedmeat_data_complete'];

    // // 딥에이징 데이터
    // deepAgingData = [];

    // if (processedmeat != null && processedmeat!.isNotEmpty) {
    //   processedmeat!.forEach((key, value) {
    //     deepAgingData!.add({
    //       'deepAgingNum': key,
    //       'date': value['sensory_eval']['deepaging_data']['date'],
    //       'minute': value['sensory_eval']['deepaging_data']['minute'],
    //       'complete': processedmeatDataComplete![key]
    //     });
    //   });
    // }
    // 완료 체크
    checkCompleted();
  }

  /// 선택된 index의 처리육 데이터 저장
  void fromJsonDeepAged(int idx) {
    seqno = int.parse('${deepAgingInfo![idx]['seqno']}');
    sensoryEval = deepAgingInfo![idx]['sensory_eval'];
    heatedSensoryEval = deepAgingInfo![idx]['heatedmeat_sensory_eval'];
    probExpt = deepAgingInfo![idx]['probexpt_data'];
    heatedProbExpt = deepAgingInfo![idx]['heatedmeat_probexpt_data'];

    // 완료 여부 확인
    checkCompleted();
  }

  // 추가 데이터 할당
  void fromJsonAdditional(String deepAgingNum) {
    if (deepAgingNum == 'RAW') {
      heatedmeat = rawmeat?['heatedmeat_sensory_eval'];
      probexptData = rawmeat?['probexpt_data'];
    } else {
      deepAgedFreshmeat = processedmeat?[deepAgingNum]['sensory_eval'];
      deepAgedImage = deepAgedFreshmeat?['imagePath'];
      heatedmeat = processedmeat?[deepAgingNum]['heatedmeat_sensory_eval'];
      probexptData = processedmeat?[deepAgingNum]['probexpt_data'];
      // 완료 체크
      if (deepAgedImage != null) {
        deepAgedImageCompleted = true;
      }
      if (deepAgedFreshmeat?['marbling'] != null &&
          deepAgedFreshmeat?['marbling'] != 0 &&
          deepAgedFreshmeat?['color'] != null &&
          deepAgedFreshmeat?['color'] != 0 &&
          deepAgedFreshmeat?['texture'] != null &&
          deepAgedFreshmeat?['texture'] != 0 &&
          deepAgedFreshmeat?['surfaceMoisture'] != null &&
          deepAgedFreshmeat?['surfaceMoisture'] != 0 &&
          deepAgedFreshmeat?['overall'] != null &&
          deepAgedFreshmeat?['overall'] != 0) {
        deepAgedFreshCompleted = true;
      }
    }
    // 완료체크
    if (heatedmeat?['flavor'] != null &&
        heatedmeat?['flavor'] != 0 &&
        heatedmeat?['juiciness'] != null &&
        heatedmeat?['juiciness'] != 0 &&
        heatedmeat?['tenderness'] != null &&
        heatedmeat?['tenderness'] != 0 &&
        heatedmeat?['umami'] != null &&
        heatedmeat?['umami'] != 0 &&
        heatedmeat?['palability'] != null &&
        heatedmeat?['palability'] != 0) {
      heatedCompleted = true;
    }
    if (probexptData?['sourness'] != null &&
        probexptData?['bitterness'] != null &&
        probexptData?['umami'] != null &&
        probexptData?['richness'] != null) {
      tongueCompleted = true;
    }
    if (probexptData?['L'] != null &&
        probexptData?['a'] != null &&
        probexptData?['b'] != null &&
        probexptData?['DL'] != null &&
        probexptData?['CL'] != null &&
        probexptData?['RW'] != null &&
        probexptData?['ph'] != null &&
        probexptData?['WBSF'] != null &&
        probexptData?['cardepsin_activity'] != null &&
        probexptData?['MFI'] != null &&
        probexptData?['Collagen'] != null) {
      labCompleted = true;
    }
  }

  // 신선육 데이터 변환
  String toJsonFresh() {
    if (seqno == 0) {
      return jsonEncode({
        'meatId': meatId,
        'createdAt': freshmeat?['createdAt'],
        'userId': userId,
        'period': freshmeat?['period'],
        'marbling': freshmeat?['marbling'],
        'color': freshmeat?['color'],
        'texture': freshmeat?['texture'],
        'surfaceMoisture': freshmeat?['surfaceMoisture'],
        'overall': freshmeat?['overall'],
        'seqno': meatModel.seqno,
      });
    } else {
      return jsonEncode({
        'meatId': meatId,
        'createdAt': deepAgedFreshmeat?['createdAt'],
        'userId': userId,
        'period': deepAgedFreshmeat?['period'],
        'marbling': deepAgedFreshmeat?['marbling'],
        'color': deepAgedFreshmeat?['color'],
        'texture': deepAgedFreshmeat?['texture'],
        'surfaceMoisture': deepAgedFreshmeat?['surfaceMoisture'],
        'overall': deepAgedFreshmeat?['overall'],
        'seqno': meatModel.seqno,
      });
    }
  }

  // 가열육 데이터 변환
  String toJsonHeated() {
    return jsonEncode({
      'meatId': meatId,
      'createdAt': heatedmeat?['createdAt'],
      'userId': userId,
      'seqno': seqno,
      'period': heatedmeat?['period'],
      'flavor': heatedmeat?['flavor'],
      'juiciness': heatedmeat?['juiciness'],
      'tenderness': heatedmeat?['tenderness'],
      'umami': heatedmeat?['umami'],
      'palability': heatedmeat?['palability']
    });
  }

  // 실험 데이터 변환
  String toJsonProbexpt() {
    return jsonEncode({
      'meatId': meatId,
      'updatedAt': probexptData?['updatedAt'],
      'userId': userId,
      'seqno': seqno,
      'period': probexptData?['period'],
      'L': probexptData?['L'],
      'a': probexptData?['a'],
      'b': probexptData?['b'],
      'DL': probexptData?['DL'],
      'CL': probexptData?['CL'],
      'RW': probexptData?['RW'],
      'ph': probexptData?['ph'],
      'WBSF': probexptData?['WBSF'],
      'cardepsin_activity': probexptData?['cardepsin_activity'],
      'MFI': probexptData?['MFI'],
      'Collagen': probexptData?['Collagen'],
      'sourness': probexptData?['sourness'],
      'bitterness': probexptData?['bitterness'],
      'umami': probexptData?['umami'],
      'richness': probexptData?['richness'],
    });
  }

  /// Meat Model 초기화
  void reset() {
    // userId, userName을 제외한 모든 데아터 초기화

    /* 육류 기본 정보 */
    meatId = null;
    createdAt = null;
    // userId = null;
    // userName = null;
    statusType = null;
    imagePath = null;
    primalValue = null;
    secondaryValue = null;
    traceNum = null;
    farmerName = null;
    farmAddr = null;
    butcheryYmd = null;
    speciesValue = null;
    sexType = null;
    gradeNum = null;
    birthYmd = null;

    /* 딥에이징 관련 데이터 */
    deepAgingInfo = null;
    sensoryEval = null;
    imgAdded = false;
    heatedSensoryEval = null;
    probExpt = null;
    heatedProbExpt = null;

    /* 데이터 입력 완료 확인 */
    basicCompleted = false;
    imageCompleted = false;
    sensoryCompleted = false;

    //

    deepAgedImage = null;
    seqno = null;
    freshmeat = null;
    deepAgedFreshmeat = null;

    // 연구 데이터 추가 입력 완료 시 저장
    deepAgingData = null;
    heatedmeat = null;
    probexptData = null;

    // 데이터 fetch 시 저장
    processedmeat = null;
    rawmeat = null;

    // // 데이터 입력 완료시 저장
    rawmeatDataComplete = false;
    processedmeatDataComplete = null;

    // 내부 데이터 입력 완료 체크
    deepAgedImageCompleted = false;

    deepAgedFreshCompleted = false;
    heatedCompleted = false;
    tongueCompleted = false;
    labCompleted = false;
  }

  /// 데이터 입력 완료 체크
  /// basicCompleted, rawImageCompleted, rawSensortCompleted
  void checkCompleted() {
    // 기본 데이터 입력 완료 확인
    // traceNum, farmerName, farmAddr,butcheryYmd, speciesValue, sexType, gradeNum, birthYmd, primalValue, secondaryValue
    basicCompleted = (traceNum != null &&
        farmerName != null &&
        farmAddr != null &&
        butcheryYmd != null &&
        speciesValue != null &&
        sexType != null &&
        gradeNum != null &&
        birthYmd != null &&
        primalValue != null &&
        secondaryValue != null);

    // 원육 사진 입력 완료 확인
    // imagePath, imgAdded
    imageCompleted = (sensoryEval != null && sensoryEval!['imagePath'] != null);

    // 원육 관능평가
    sensoryCompleted = (sensoryEval != null &&
        sensoryEval!['marbling'] != null &&
        sensoryEval!['color'] != null &&
        sensoryEval!['texture'] != null &&
        sensoryEval!['surfaceMoisture'] != null &&
        sensoryEval!['overall'] != null);

    // 원육/처리육 전자혀 데이터
    tongueCompleted = (probExpt != null &&
        probExpt!['sourness'] != null &&
        probExpt!['bitterness'] != null &&
        probExpt!['umami'] != null &&
        probExpt!['richness'] != null);

    // 원육/처리육 실험 데이터
    labCompleted = (probExpt != null &&
        probExpt!['L'] != null &&
        probExpt!['a'] != null &&
        probExpt!['b'] != null &&
        probExpt!['DL'] != null &&
        probExpt!['CL'] != null &&
        probExpt!['RW'] != null &&
        probExpt!['ph'] != null &&
        probExpt!['WBSF'] != null &&
        probExpt!['cardepsin_activity'] != null &&
        probExpt!['MFI'] != null &&
        probExpt!['Collagen'] != null);

    // 가열육 단면 촬영
    heatedImageCompleted =
        (heatedSensoryEval != null && heatedSensoryEval!['imagePath'] != null);

    // 가열육 관능평가
    heatedSensoryCompleted = (heatedSensoryEval != null &&
        heatedSensoryEval!['flavor'] != null &&
        heatedSensoryEval!['juiciness'] != null &&
        heatedSensoryEval!['tenderness'] != null &&
        heatedSensoryEval!['umami'] != null &&
        heatedSensoryEval!['palatability'] != null);

    // 가열육 전자혀 데이터
    heatedTongueCompleted = (heatedProbExpt != null &&
        heatedProbExpt!['sourness'] != null &&
        heatedProbExpt!['bitterness'] != null &&
        heatedProbExpt!['umami'] != null &&
        heatedProbExpt!['richness'] != null);

    // 가열육 실헙 데이터
    heatedLabCompleted = (heatedProbExpt != null &&
        heatedProbExpt!['L'] != null &&
        heatedProbExpt!['a'] != null &&
        heatedProbExpt!['b'] != null &&
        heatedProbExpt!['DL'] != null &&
        heatedProbExpt!['CL'] != null &&
        heatedProbExpt!['RW'] != null &&
        heatedProbExpt!['ph'] != null &&
        heatedProbExpt!['WBSF'] != null &&
        heatedProbExpt!['cardepsin_activity'] != null &&
        heatedProbExpt!['MFI'] != null &&
        heatedProbExpt!['Collagen'] != null);
  }

  // text code
  @override
  String toString() {
    return 'meatId: $meatId,'
        'seqno: $seqno,'
        'freshmeat: $freshmeat,'
        'deepAgedFreshmeat: $deepAgedFreshmeat,'
        'statusType: $statusType,'

        // 연구 데이터 추가 입력 완료 시 저장
        'deepAging: $deepAgingData,'
        'heatedmeat: $heatedmeat,'
        'probexptData: $probexptData,'

        // 데이터 fetch 시 저장
        'processedmeat: $processedmeat,'
        'rawmeat: $rawmeat,'

        // // 데이터 입력 완료시 저장
        'rawmeatDataComplete: $rawmeatDataComplete,'
        'processedmeatDataComplete: $processedmeatDataComplete,';
  }
}

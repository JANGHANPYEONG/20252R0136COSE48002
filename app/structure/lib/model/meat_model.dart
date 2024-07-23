//
//
// 육류 모델
//
//

import 'dart:convert';

import 'package:flutter/material.dart';
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
  /// <br /> Map<String, dynamic> heated_probexpt_data
  List<dynamic>? deepAgingInfo;

  /// 원육 관능평가 데이터
  ///
  /// String meatId
  /// <br /> String userId
  /// <br /> String userName
  /// <br /> String imagePath,
  /// <br /> String filmedAt, (yyyy-MM-dd hh:mm:ss)
  /// <br /> int seqno
  /// <br /> int period
  /// <br /> Sring createdAt (yyyy-MM-dd hh:mm:ss)
  /// <br /> double marbling
  /// <br /> double color
  /// <br /> double texture
  /// <br /> double surfaceMoisture
  /// <br /> double overall
  Map<String, dynamic>? sensoryEval;
  // 이미지 새로 추가 여부
  bool? imgAdded;

  Map<String, dynamic>? heatedSensoryEval;
  Map<String, dynamic>? probExpt;
  Map<String, dynamic>? heatedProbExpt;

  /* 데이터 입력 완료 확인 */
  /// 육류 기본정보 입력 완료 여부
  ///
  /// traceNum, farmerName, farmAddr,butcheryYmd, speciesValue, sexType, gradeNum, birthYmd, primalValue, secondaryValue
  bool basicCompleted = false;

  /// 원육 이미지 등록 완료 여부
  ///
  /// imagePath, imgAdded
  bool rawImageCompleted = false;

  /// 원육 관능평가 등록 완료 여부
  ///
  /// marbling, color, texture, surfaceMoisture, overall
  bool rawSensoryCompleted = false;

  // 미완료
  // 육류 이미지 경로
  String? deepAgedImage;

  // 딥에이징 차수
  int? seqno;

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
  bool tongueCompleted = false;
  bool labCompleted = false;

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
      'rawImageCompleted': rawImageCompleted,
      'rawSensoryCompleted': rawSensoryCompleted
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
    rawImageCompleted = jsonData['rawImageCompleted'];
    rawSensoryCompleted = jsonData['rawSensoryCompleted'];
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
    deepAgingInfo = jsonData['deepAgingInfo'].length == 1
        ? null
        : jsonData['deepAgingInfo'].sublist(1);
    sensoryEval = jsonData['deepAgingInfo'][0]['sensoryEval'];

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
    imgAdded = null;
    heatedSensoryEval = null;
    probExpt = null;
    heatedProbExpt = null;

    /* 데이터 입력 완료 확인 */
    basicCompleted = false;
    rawImageCompleted = false;
    rawSensoryCompleted = false;

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
    rawImageCompleted = (sensoryEval != null &&
        sensoryEval!['imagePath'] != null &&
        imgAdded != null);

    // 원육 관능평가
    rawSensoryCompleted = (sensoryEval != null &&
        sensoryEval!['marbling'] != null &&
        sensoryEval!['color'] != null &&
        sensoryEval!['texture'] != null &&
        sensoryEval!['surfaceMoisture'] != null &&
        sensoryEval!['overall'] != null);

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

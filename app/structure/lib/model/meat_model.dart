//
//
// 육류 모델
//
//

import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

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
  /// <br /> Map<String, dynamic> heatedmeat_sensory_eval
  /// <br /> Map<String, dynamic> probexpt_data
  /// <br /> Map<String, dynamic> heatedmeat_probexpt_data
  List<dynamic>? deepAgingInfo;

  /// 선택된 데이터의 seqno
  int? seqno;

  /// 선택된 데이터의 deepaging 생성 날짜
  String? deepAgingCreatedAt;

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
  /// <br /> double tenderness0
  /// <br /> double tenderness3
  /// <br /> double tenderness7
  /// <br /> double tenderness14
  /// <br /> double tenderness21
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
  /// flavor, juiciness, tenderness0, umami, palatability
  bool heatedSensoryCompleted = false;

  /// 가열육 전자혀 데이터 등록 완료 여부
  ///
  /// sourness, bitterness, umami, richness
  bool heatedTongueCompleted = false;

  /// 가열육 실험 데이터 등록 완료 여부
  ///
  /// L, a, b, DL, CL, RW, ph, WBSF, cardepsin_activity, MFI, Collagen
  bool heatedLabCompleted = false;

  /// 원육 추가정보 입력 완료 여부
  ///
  /// tongueCompleted, labCompleted, heatedImageCompleted, heatedSensoryCompleted, heatedTongueCompleted, heatedLabCompleted
  bool rawCompleted = false;

  List<bool> processedCompleted = [];

  // Constructor
  MeatModel({
    this.meatId,
    this.createdAt,
    this.userId,
    this.userName,
    this.statusType,
    this.imagePath,
    this.primalValue,
    this.secondaryValue,
    this.traceNum,
    this.farmerName,
    this.farmAddr,
    this.butcheryYmd,
    this.speciesValue,
    this.sexType,
    this.gradeNum,
    this.birthYmd,
    this.deepAgingInfo,
    this.seqno,
    this.deepAgingCreatedAt,
    this.sensoryEval,
    this.heatedSensoryEval,
    this.probExpt,
    this.heatedProbExpt,
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
      'meatId': sensoryEval?['meatId'],
      'userId': sensoryEval?['userId'],
      'seqno': sensoryEval?['seqno'],
      'imgAdded': imgAdded,
      'filmedAt': sensoryEval?['filmedAt'],
      'sensoryData': {
        'marbling': sensoryEval?['marbling'],
        'color': sensoryEval?['color'],
        'texture': sensoryEval?['texture'],
        'surfaceMoisture': sensoryEval?['surfaceMoisture'],
        'overall': sensoryEval?['overall'],
      }
    });
  }

  /// 가열육 관능평가 데이터 정보 json 변환
  ///
  /// meatId, userId, seqno, imgAdded, filmedAt, marbling, color, texture, surfaceMoisture, overall
  String toJsonHeatedSensory() {
    return jsonEncode({
      'meatId': heatedSensoryEval?['meatId'],
      'userId': heatedSensoryEval?['userId'],
      'seqno': heatedSensoryEval?['seqno'],
      'imgAdded': heatedImgAdded,
      'filmedAt': heatedSensoryEval?['filmedAt'],
      'heatedmeatSensoryData': {
        'flavor': heatedSensoryEval?['flavor'],
        'juiciness': heatedSensoryEval?['juiciness'],
        'tenderness0': heatedSensoryEval?['tenderness0'],
        'tenderness3': heatedSensoryEval?['tenderness3'],
        'tenderness7': heatedSensoryEval?['tenderness7'],
        'tenderness14': heatedSensoryEval?['tenderness14'],
        'tenderness21': heatedSensoryEval?['tenderness21'],
        'umami': heatedSensoryEval?['umami'],
        'palatability': heatedSensoryEval?['palatability'],
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
      'heatedmeat_sensory_eval': null,
      'probexpt_data': null,
      'heatedmeat_probexpt_data': null,
    };

    deepAgingInfo!.add(info);
  }

  /// 새로 추가된 sensoryEval 데이터를 로컬 deepAgingInfo에 추가하는 함수
  /// <br /> DB에 데이터 전송 후 200인 경우에만 실행
  void updateSeonsory() {
    final info = deepAgingInfo!
        .firstWhere((item) => '${item['seqno']}' == '${sensoryEval!['seqno']}');
    info['sensory_eval'] = sensoryEval;
  }

  /// 새로 추가된 heatedSensoryEval 데이터를 로컬 deepAgingInfo에 추가하는 함수
  /// <br /> DB에 데이터 전송 후 200인 경우에만 실행
  void updateHeatedSeonsory() {
    final info = deepAgingInfo!.firstWhere(
        (item) => '${item['seqno']}' == '${heatedSensoryEval!['seqno']}');
    info['heatedmeat_sensory_eval'] = heatedSensoryEval;
  }

  /// 새로 추가된 probExpt 데이터를 로컬 deepAgingInfo에 추가하는 함수
  /// <br /> DB에 데이터 전송 후 200인 경우에만 실행
  void updateProbExpt() {
    final info = deepAgingInfo!
        .firstWhere((item) => '${item['seqno']}' == '${probExpt!['seqno']}');
    info['probexpt_data'] = probExpt;
  }

  /// 새로 추가된 heatedProbExpt 데이터를 로컬 deepAgingInfo에 추가하는 함수
  /// <br /> DB에 데이터 전송 후 200인 경우에만 실행
  void updateHeatedProbExpt() {
    final info = deepAgingInfo!.firstWhere(
        (item) => '${item['seqno']}' == '${heatedProbExpt!['seqno']}');
    info['heatedmeat_probexpt_data'] = heatedProbExpt;
  }

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

    // 완료 체크
    checkCompleted();
  }

  /// 선택된 index의 처리육 데이터 저장
  void fromJsonDeepAged(int idx) {
    seqno = int.parse('${deepAgingInfo![idx]['seqno']}');
    deepAgingCreatedAt = deepAgingInfo![idx]['date'];
    sensoryEval = deepAgingInfo![idx]['sensory_eval'];
    heatedSensoryEval = deepAgingInfo![idx]['heatedmeat_sensory_eval'];
    probExpt = deepAgingInfo![idx]['probexpt_data'];
    heatedProbExpt = deepAgingInfo![idx]['heatedmeat_probexpt_data'];

    // 완료 여부 확인
    checkCompleted();
  }

  /// Meat Model 초기화
  void reset() {
    // userId, userName을 제외한 모든 데아터 초기화

    /* 육류 기본 정보 */
    meatId = null;
    createdAt = null;
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
    seqno = null;
    deepAgingCreatedAt = null;
    sensoryEval = null;
    imgAdded = false;
    heatedSensoryEval = null;
    heatedImgAdded = false;
    probExpt = null;
    heatedProbExpt = null;

    /* 데이터 입력 완료 확인 */
    basicCompleted = false;
    rawCompleted = false;
    processedCompleted = [];
    imageCompleted = false;
    sensoryCompleted = false;
    tongueCompleted = false;
    labCompleted = false;
    heatedImageCompleted = false;
    heatedSensoryCompleted = false;
    heatedTongueCompleted = false;
    heatedLabCompleted = false;
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
        heatedSensoryEval!['tenderness0'] != null &&
        // heatedSensoryEval!['tenderness3'] != null &&
        // heatedSensoryEval!['tenderness7'] != null &&
        // heatedSensoryEval!['tenderness14'] != null &&
        // heatedSensoryEval!['tenderness21'] != null &&
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

    /* 추기정보 입력 완료 여부 */
    // 원육 추가정보 입력 완료 확인
    rawCompleted = (tongueCompleted &&
        labCompleted &&
        heatedImageCompleted &&
        heatedSensoryCompleted &&
        heatedTongueCompleted &&
        heatedLabCompleted);
  }

  // text code
  @override
  String toString() {
    return 'meatId: $meatId,'
        'userId: $userId,'
        'seqno: $seqno,'
        'primalValue: $primalValue,'
        'secondaryValue: $secondaryValue,'
        'traceNum: $traceNum,'
        'farmerName: $farmerName,'
        'farmAddr: $farmAddr,'
        'butcheryYmd: $butcheryYmd,'
        'speciesValue: $speciesValue,'
        'sexType: $sexType,'
        'gradeNum: $gradeNum,'
        'birthYmd: $birthYmd,'
        'statusType: $statusType,'
        'sensoryEval: $sensoryEval,'
        'heatedSensoryEval: $heatedSensoryEval,'
        'probExpt: $probExpt,'
        'heatedProbExpt: $heatedProbExpt';
  }
}

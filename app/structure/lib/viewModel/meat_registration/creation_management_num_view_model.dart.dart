import 'dart:convert';
import 'dart:io';
import 'dart:ui';

import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:crypto/crypto.dart';
import 'package:firebase_storage/firebase_storage.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:path_provider/path_provider.dart';
import 'package:qr_flutter/qr_flutter.dart';
import 'package:structure/config/usefuls.dart';
import 'package:structure/dataSource/local_data_source.dart';
import 'package:structure/dataSource/remote_data_source.dart';
import 'package:structure/model/meat_model.dart';
import 'package:structure/model/user_model.dart';

class CreationManagementNumViewModel with ChangeNotifier {
  MeatModel meatModel;
  UserModel userModel;
  BuildContext context;

  CreationManagementNumViewModel(this.meatModel, this.userModel, this.context) {
    _initialize();
  }
  bool isLoading = true;

  String managementNum = '-';
  bool isFetchLoading = false;
  FirebaseFirestore firestore = FirebaseFirestore.instance;

  Future<void> _initialize() async {
    isLoading = true;
    notifyListeners();

    // 관리번호 생성
    await _createManagementNum();

    // 이미지 저장
    await _sendImageToFirebase();

    // 데이터 전송
    await _sendMeatData();

    // 연구원의 경우 바로 데이터 승인
    if (userModel.type != 'Normal') {
      try {
        final response = await RemoteDataSource.confirmMeatData(managementNum);

        if (response != 200) throw ErrorDescription(response);
      } catch (e) {
        debugPrint('Error: $e');
      }
    }

    isLoading = false;
    notifyListeners();
  }

  /// 1. 관리번호 생성
  /// traceNum, speciesValue, primalValue, secondayValue를 토대로 관리 번호를 생성함
  Future<void> _createManagementNum() async {
    if (meatModel.traceNum != null &&
        meatModel.speciesValue != null &&
        meatModel.primalValue != null &&
        meatModel.secondaryValue != null) {
      // 관리번호: 이력코드-생성일자-종-대분할-소분할
      String createdAt = Usefuls.getCurrentDate();
      String originalString =
          '${meatModel.traceNum!}-$createdAt-${meatModel.speciesValue!}-${meatModel.primalValue!}-${meatModel.secondaryValue!}';

      // 해시함수로 meatId 생성
      managementNum = _hashStringTo12Digits(originalString);
      // 생성한 meatId 저장
      meatModel.meatId = managementNum;
      meatModel.sensoryEval!['meatId'] = managementNum;
    } else {
      // 데이터 입력이 제대로 되지 않았을 때 에러 반환
      debugPrint('Error creating managementNum');
    }
  }

  /// 관리번호 해시 함수
  String _hashStringTo12Digits(String input) {
    // 입력 문자열을 UTF-8로 인코딩
    List<int> bytes = utf8.encode(input);

    // 해시 알고리즘으로 SHA-256을 선택
    Digest digest = sha256.convert(bytes);

    // 해시 값을 16진수로 변환
    String hexHash = digest.toString();

    // 앞에서부터 12자리를 추출
    String twelveDigits = hexHash.substring(0, 12);

    return twelveDigits;
  }

  /// 2. 이미지를 파이어베이스에 저장
  Future<void> _sendImageToFirebase() async {
    try {
      // fire storage에 육류 이미지 저장
      final refMeatImage = FirebaseStorage.instance
          .ref()
          .child('sensory_evals/$managementNum-0.png');

      await refMeatImage.putFile(
        File(meatModel.sensoryEval!['imagePath']),
        SettableMetadata(contentType: 'image/jpeg'),
      );

      // QR 생성 후 firestore에 업로드
      await uploadQRCodeImageToStorage();
    } catch (e) {
      debugPrint('Error uploading image to firebase: $e');
      if (context.mounted) context.go('/home/registration-fail');
    }
  }

  /// 2.1 QR 생성 및 전송
  Future<void> uploadQRCodeImageToStorage() async {
    // QR 코드 생성
    final qrPainter = QrPainter(
      data: managementNum,
      version: QrVersions.auto,
      gapless: true,
    );

    // 이미지 파일로 변환
    final image = await qrPainter.toImage(200);
    final byteData = await image.toByteData(format: ImageByteFormat.png);
    final bytes = byteData!.buffer.asUint8List();

    // firebase storage에 저장
    final storageRef =
        FirebaseStorage.instance.ref().child('qr_codes/$managementNum.png');
    await storageRef.putData(bytes);

    // 프린트를 위해 이미지 위치 저장
    final directory = await getTemporaryDirectory();
    final imgPath = '${directory.path}/qr-${DateTime.now()}.jpeg';
    meatModel.imagePath = imgPath;

    final imgFile = File(imgPath);
    await imgFile.writeAsBytes(bytes);
  }

  /// 3. 육류 정보를 서버로 전송
  Future<void> _sendMeatData() async {
    try {
      // 육류 기본 정보 입력
      final response1 =
          await RemoteDataSource.createMeatData(null, meatModel.toJsonBasic());
      // 원육 관능평가 데이터 입력
      final response2 = await RemoteDataSource.createMeatData(
          'sensory-eval', meatModel.toJsonSensory());

      if (response1 == 200 && response2 == 200) {
        // 육류 등록 성공
        // 임시저장된 데이터 삭제
        await LocalDataSource.deleteLocalData(meatModel.userId!);

        isLoading = false;
        notifyListeners();
      } else {
        throw ErrorDescription(response2);
      }
    } catch (e) {
      debugPrint('Error: $e');
      if (context.mounted) context.go('/home/registration-fail');
    }
  }

  void clickedQR() {
    context.go('/home/success-registration/qr');
  }

  void clickedHomeButton() {
    context.go('/home');
  }
}

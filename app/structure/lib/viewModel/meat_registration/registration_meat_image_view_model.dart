//
//
// 육류 이미지 등록 viewModel.
//
//

import 'dart:convert';
import 'dart:io';
import 'package:go_router/go_router.dart';

import 'package:firebase_storage/firebase_storage.dart';
import 'package:flutter/material.dart';
import 'package:structure/components/custom_dialog.dart';
import 'package:structure/components/custom_pop_up.dart';
import 'package:structure/config/userfuls.dart';
import 'package:structure/dataSource/remote_data_source.dart';
import 'package:structure/model/meat_model.dart';
import 'package:structure/dataSource/local_data_source.dart';
import 'package:structure/model/user_model.dart';

class RegistrationMeatImageViewModel with ChangeNotifier {
  final MeatModel meatModel;
  final UserModel userModel;

  RegistrationMeatImageViewModel(this.meatModel, this.userModel) {
    _initialize();
  }
  bool isLoading = false;

  // 초기 변수
  String date = '-'; // 촬영 날짜
  String userName = '-'; // 촬영자

  late DateTime time;

  // 사진 관련 변수
  String? imgPath;
  File? imgFile;
  bool imgAdded = false;

  late BuildContext _context;

  /// 초기 할당
  void _initialize() async {
    isLoading = true;
    notifyListeners();

    // 임시저장 데이터 불러오기
    if (meatModel.sensoryEval != null) {
      userName = meatModel.sensoryEval!['userName'];
      imgPath = meatModel.sensoryEval!['imagePath'];

      // TODO : filmedAt 추가
      time = DateTime.now();
      date =
          '${time.year}.${time.month.toString().padLeft(2, '0')}.${time.day}';
    }

    // if (meatModel.seqno == 0) {
    //   // 원육 데이터
    //   // 수정
    //   imgPath = meatModel.imagePath;
    //   if (imgPath != null && meatModel.freshmeat != null) {
    //     if (meatModel.freshmeat!['userId'] == userModel.userId) {
    //       // 로그인된 유저와 id가 같으면 그냥 userModel에서 이름 불러오기
    //       userName = userModel.name ?? '-';
    //     } else {
    //       // 다른 유저면 api 호출해서 이름 정보 가져오기
    //       dynamic user = await RemoteDataSource.getUserInfo(
    //           meatModel.freshmeat!['userId']);
    //       userName = user['name'] ?? '-';
    //     }

    //     if (meatModel.freshmeat!['createdAt'] != null) {
    //       Usefuls.parseDate(meatModel.freshmeat!['createdAt']);
    //       date =
    //           '${time.year}.${time.month..toString().padLeft(2, '0')}.${time.day}';
    //     }
    //   }
    // } else {
    //   // 처리육 데이터
    //   imgPath = meatModel.deepAgedImage;
    //   if (imgPath != null && meatModel.deepAgedFreshmeat != null) {
    //     if (meatModel.deepAgedFreshmeat!['userId'] == userModel.userId) {
    //       // 로그인된 유저와 id가 같으면 그냥 userModel에서 이름 불러오기
    //       userName = userModel.name ?? '-';
    //     } else {
    //       // 다른 유저면 api 호출해서 이름 정보 가져오기
    //       dynamic user = await RemoteDataSource.getUserInfo(
    //           meatModel.deepAgedFreshmeat!['userId']);
    //       userName = user['name'] ?? '-';
    //     }

    //     if (meatModel.deepAgedFreshmeat!["createdAt"] != null) {
    //       Usefuls.parseDate(meatModel.deepAgedFreshmeat!["createdAt"]);
    //       date =
    //           '${time.year}.${time.month.toString().padLeft(2, '0')}.${time.day}';
    //     }
    //   }
    // }

    isLoading = false;
    notifyListeners();
  }

  /// 촬영한 이미지가 있는지 확인하는 함수
  bool imageCheck() {
    return imgPath != null;
  }

  /// 뒤로가기 버튼
  VoidCallback? backBtnPressed(BuildContext context) {
    return () => showExitDialog(context);
  }

  /// 촬영자, 촬영 날짜 설정
  void _setInfo() {
    time = DateTime.now();
    date = '${time.year}.${time.month.toString().padLeft(2, '0')}.${time.day}';
    userName = userModel.name ?? '-';
  }

  /// 이미지 촬영을 위한 메소드
  /// 카메라 실행 후 촬영한 사진 경로를 받아옴
  Future<void> pickImage(BuildContext context) async {
    String? tempImgPath = await context.push('/home/registration/image/camera');

    // 반환된 사진이 있으면 저장 팝업 생성
    if (tempImgPath != null) {
      if (context.mounted) {
        showSaveImageDialog(
          context,
          tempImgPath,
          () => context.pop(),
          () {
            isLoading = true; // 로딩 활성화
            notifyListeners();

            // 정보 저장
            imgPath = tempImgPath;
            imgFile = File(tempImgPath);
            imgAdded = true;
            _setInfo();

            isLoading = false; // 로딩 비활성화
            notifyListeners();
            context.pop();
          },
        );
      }
    } else {
      // 사진 찍기 오류
      // TODO : 이미지 촬영 오류 팝업 띄우기
      debugPrint('Image error');
    }
  }

  /// 사진 초기화
  void deleteImage(BuildContext context) {
    showDeletePhotoDialog(context, () {
      imgPath = null;
      imgFile = null;
      imgAdded = false;
      date = '-';
      userName = '-';

      notifyListeners();
      context.pop();
    });
  }

  /// 데이터 등록
  Future<void> saveMeatData(BuildContext context) async {
    isLoading = true;
    notifyListeners();

    try {
      if (meatModel.meatId == null) {
        // 새로운 이미지 등록
        meatModel.imgAdded = true; // 새로 등록할때는 항상 true
        meatModel.sensoryEval = {};
        meatModel.sensoryEval!['userId'] = userModel.userId;
        meatModel.sensoryEval!['userName'] = userModel.name;
        meatModel.sensoryEval!['imagePath'] = imgPath;
        meatModel.sensoryEval!['filmedAt'] = Usefuls.getCurrentDate();
        meatModel.sensoryEval!['seqno'] = 0;
      }

      if (meatModel.seqno == 0) {
        // 원육
        // meatModel.imagePath = imgPath;
        // meatModel.freshmeat ??= {};
        // meatModel.freshmeat!['userId'] = meatModel.userId;
        // meatModel.freshmeat!['createdAt'] = Usefuls.getCurrentDate();
        if (meatModel.meatId != null) {
          // 수정
          // meatModel이 존재할 때는 바로 이미지 적용
          await _sendImageToFirebase();
          await RemoteDataSource.createMeatData(
              'sensory-eval', meatModel.toJsonFresh());

          // 팝업 띄우기 전에 isLoading 끄기
          isLoading = false;
          notifyListeners();
        }
      } else {
        // 처리육
        meatModel.deepAgedImage = imgPath;
        meatModel.deepAgedFreshmeat ??= {};
        meatModel.deepAgedFreshmeat!['userId'] = meatModel.userId;
        meatModel.deepAgedFreshmeat!['createdAt'] = Usefuls.getCurrentDate();
        await _sendImageToFirebase();
        await RemoteDataSource.createMeatData(
            'sensory-eval',
            jsonEncode({
              "meatId": meatModel.meatId,
              "createdAt": meatModel.deepAgedFreshmeat!['createdAt'],
              "userId": meatModel.deepAgedFreshmeat!['userId'],
              "seqno": meatModel.seqno
            }));
      }
      meatModel.checkCompleted();

      // 임시저장
      await tempSave();
      _context = context; // movePage를 위한 context 설정

      isLoading = false;
      notifyListeners();

      _movePage();
    } catch (e) {
      debugPrint('에러발생: $e');
    }
  }

  /// 페이지 이동
  void _movePage() {
    if (meatModel.seqno == 0) {
      // 원육
      if (meatModel.meatId == null) {
        //등록
        _context.go('/home/registration');
      } else {
        // 수정
        showDataManageSucceedPopup(_context, () {
          _context.go('/home/data-manage-normal/edit');
        });
      }
    } else {
      // 처리육
      _context.go('/home/data-manage-researcher/add/processed-meat');
    }
  }

  /// 이미지를 파이어베이스에 저장
  Future<void> _sendImageToFirebase() async {
    try {
      // fire storage에 육류 이미지 저장
      final refMeatImage = FirebaseStorage.instance
          .ref()
          .child('sensory_evals/${meatModel.meatId}-${meatModel.seqno}.png');

      // if (imgPath!.contains('http')) {
      //   // db 사진
      //   final http.Response response =
      //       await http.get(Uri.parse(meatModel.imagePath!));
      //   final Uint8List imageData = Uint8List.fromList(response.bodyBytes);
      //   await refMeatImage.putData(
      //     imageData,
      //     SettableMetadata(contentType: 'image/jpeg'),
      //   );
      // } else

      // 이미지가 새롭게 수정된 경우에만 firebase에 업로드
      if (imgAdded) {
        await refMeatImage.putFile(
          imgFile!,
          SettableMetadata(contentType: 'image/jpeg'),
        );
      }
    } catch (e) {
      debugPrint('Error: $e');
      // 에러 팝업
      if (_context.mounted) showFileUploadFailPopup(_context);
    }
  }

  /// 임시저장
  Future<void> tempSave() async {
    try {
      dynamic response = await LocalDataSource.saveDataToLocal(
          meatModel.toJsonTemp(), meatModel.userId!);
      if (response == null) throw Error();
    } catch (e) {
      debugPrint('Error: $e');
    }
  }
}

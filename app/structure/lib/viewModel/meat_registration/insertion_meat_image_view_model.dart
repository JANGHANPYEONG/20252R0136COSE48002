//
//
// 육류 이미지 등록 viewModel.
//
//

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

class InsertionMeatImageViewModel with ChangeNotifier {
  final MeatModel meatModel;
  final UserModel userModel;
  final bool isRaw;

  InsertionMeatImageViewModel(this.meatModel, this.userModel, this.isRaw) {
    _initialize();
  }
  bool isLoading = false;
  late BuildContext _context;

  String title = '단면 촬영';
  String saveBtnText = '완료';

  // 초기 변수
  String filmedAt = '-'; // 촬영된 날짜
  String date = '-'; // 화면에 표시하는 촬영 날짜
  String userName = '-'; // 촬영자

  // 사진 관련 변수
  String? imgPath;
  File? imgFile;
  bool imgAdded = false;

  /// 초기 할당
  void _initialize() async {
    isLoading = true;
    notifyListeners();

    if (isRaw) {
      // 원육/처리육
      // 임시저장/수정 데이터 불러오기
      if (meatModel.sensoryEval != null && meatModel.imageCompleted) {
        userName = meatModel.sensoryEval!['userName'];
        imgPath = meatModel.sensoryEval!['imagePath'];
        filmedAt = meatModel.sensoryEval!['filmedAt'];
        date = Usefuls.parseDate(meatModel.sensoryEval!['filmedAt']);
        saveBtnText = '수정사항 저장';
      }

      title = meatModel.seqno == 0 ? '원육 단면 촬영' : '처리육 단면 촬영';
    } else {
      if (meatModel.heatedSensoryEval != null &&
          meatModel.heatedImageCompleted) {
        userName = meatModel.heatedSensoryEval!['userName'];
        imgPath = meatModel.heatedSensoryEval!['imagePath'];
        filmedAt = meatModel.heatedSensoryEval!['filmedAt'];
        date = Usefuls.parseDate(meatModel.heatedSensoryEval!['filmedAt']);
        saveBtnText = '수정사항 저장';
      }

      title = '가열육 단면 촬영';
    }

    isLoading = false;
    notifyListeners();
  }

  /// 뒤로가기 버튼
  VoidCallback? backBtnPressed(BuildContext context) {
    return () => showExitDialog(context);
  }

  /// 촬영자, 촬영 날짜 설정
  void _setInfo() {
    filmedAt = Usefuls.getCurrentDate();
    date = Usefuls.parseDate(filmedAt);
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

    // sensoryEval이 없으면 post로 진행
    bool isPost = false;

    if (isRaw) {
      // 원육/처리육
      // 원육 등록의 경우 이미지 등록을 해야 관능평가가 가능하기 때문에 이미지 등록 시점에서는 sensoryEval = null
      if (meatModel.sensoryEval == null) {
        // POST의 경우 신규 데이터 생상
        isPost = true;

        meatModel.sensoryEval = {};
        // 처리육의 경우 meatId는 있음. 원육의 경우 null
        meatModel.sensoryEval!['meatId'] = meatModel.meatId;
        meatModel.sensoryEval!['seqno'] = meatModel.seqno;
      }
      meatModel.sensoryEval!['userId'] = userModel.userId;
      meatModel.sensoryEval!['userName'] = userModel.name;
      meatModel.sensoryEval!['imagePath'] = imgPath; // 로컬을 위한 imgagePath 저장
      meatModel.sensoryEval!['filmedAt'] = filmedAt;
      meatModel.imgAdded = imgAdded;
    } else {
      if (meatModel.heatedSensoryEval == null) {
        // POST의 경우 신규 데이터 생상
        isPost = true;

        meatModel.heatedSensoryEval = {};
        meatModel.heatedSensoryEval!['meatId'] = meatModel.meatId;
        meatModel.heatedSensoryEval!['seqno'] = meatModel.seqno;
      }
      meatModel.heatedSensoryEval!['userId'] = userModel.userId;
      meatModel.heatedSensoryEval!['userName'] = userModel.name;
      meatModel.heatedSensoryEval!['imagePath'] = imgPath;
      meatModel.heatedSensoryEval!['filmedAt'] = filmedAt;
      meatModel.heatedImgAdded = imgAdded;
    }

    meatModel.checkCompleted();

    // API 전송은 원육 등록이 아닌 경우에만 (meatId != null)
    // 원육은 creation_management_num에서 처리
    if (meatModel.meatId != null) {
      try {
        // 이미지 업로드 먼저
        await _sendImageToFirebase();

        dynamic response;

        if (isRaw) {
          // 처리육
          if (isPost) {
            response = await RemoteDataSource.createMeatData(
                'sensory-eval', meatModel.toJsonSensory());
          } else {
            // 처리육 patch
            response = await RemoteDataSource.patchMeatData(
                'sensory-eval', meatModel.toJsonSensory());
          }
        } else {
          // 가열육
          if (isPost) {
            response = await RemoteDataSource.createMeatData(
                'heatedmeat-eval', meatModel.toJsonHeatedSensory());
          } else {
            response = await RemoteDataSource.patchMeatData(
                'heatedmeat-eval', meatModel.toJsonHeatedSensory());
          }
        }

        if (response == 200) {
          if (isRaw) {
            meatModel.updateSeonsory();
          } else {
            meatModel.updateHeatedSeonsory();
          }
        } else {
          // TODO : 입력한 데이터 초기화
          throw ErrorDescription(response);
        }
      } catch (e) {
        debugPrint('Error: $e');
        if (context.mounted) showErrorPopup(context);
      }
    } else {
      // 신규 생성일때만 임시저장
      await tempSave();
    }

    isLoading = false;
    notifyListeners();

    _context = context; // movePage를 위한 context 설정
    _movePage();
  }

  /// 페이지 이동
  void _movePage() {
    if (meatModel.meatId == null) {
      // 신규 등록
      _context.go('/home/registration');
    } else {
      // 원육 수정
      if (meatModel.seqno == 0 && isRaw) {
        showDataManageSucceedPopup(_context, () {
          _context.go('/home/data-manage-normal/edit');
        });
      } else if (meatModel.seqno == 0) {
        _context.go('/home/data-manage-researcher/add/raw-meat');
      } else {
        // 처리육/가열육
        _context.go('/home/data-manage-researcher/add/processed-meat');
      }
    }
  }

  /// 이미지를 파이어베이스에 저장
  ///
  /// imgAdded가 참일 때만 파이어베이스에 업로드
  Future<void> _sendImageToFirebase() async {
    try {
      // fire storage에 육류 이미지 저장
      Reference refMeatImage;
      if (isRaw) {
        refMeatImage = FirebaseStorage.instance
            .ref()
            .child('sensory_evals/${meatModel.meatId}-${meatModel.seqno}.png');
      } else {
        refMeatImage = FirebaseStorage.instance.ref().child(
            'heatedmeat_sensory_evals/${meatModel.meatId}-${meatModel.seqno}.png');
      }

      // 이미지가 새롭게 수정된 경우에만 firebase에 업로드
      if (imgAdded) {
        // TODO : 이미지 업데이트 확인
        await refMeatImage.putFile(
          imgFile!,
          SettableMetadata(contentType: 'image/jpeg'),
        );
      }
    } catch (e) {
      debugPrint('Error: $e');
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
      // TODO : 임시저장 에러 메시지 팝업
    }
  }
}

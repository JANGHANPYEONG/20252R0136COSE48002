import 'dart:io';

import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:path_provider/path_provider.dart';
import 'package:structure/components/custom_pop_up.dart';

class CameraViewModel with ChangeNotifier {
  BuildContext context;
  CameraViewModel({required this.context}) {
    _initialize();
  }

  late List<CameraDescription> _cameras;
  late CameraController controller;

  bool isLoaded = false;
  bool canTakePicture = false;
  bool isFlashOn = false; // Flash on/off

  Future<void> _initialize() async {
    // 사용 가능한 카메라 불러오기
    _cameras = await availableCameras();
    // 후면 카메라를 기본으로 설정
    controller = CameraController(_cameras[0], ResolutionPreset.max,
        imageFormatGroup: ImageFormatGroup.jpeg, enableAudio: false);

    await controller.initialize().catchError((e) {
      if (e is CameraException && e.code == 'CameraAccessDenied') {
        // 카메라 권한 설정
        debugPrint('Camera access denied');
        // TODO : 카메라 권한 팝업
      } else {
        // 카메라 오류
        debugPrint('Camera error: $e');
        if (context.mounted) showErrorPopup(context, error: e.toString());
      }
    });

    // controller initialize 후 초기 값 설정
    controller.setFlashMode(FlashMode.off); // 플래시 끄기

    // 카메라 설정 완료
    isLoaded = controller.value.isInitialized;
    canTakePicture = isLoaded;
    notifyListeners();
  }

  @override
  void dispose() {
    // 카메라 controller 햐제
    controller.dispose();
    super.dispose();
  }

  /// 사진 촬영
  Future<void> takePicture() async {
    // 카메라 init 오류 또는 사진 찍는 중
    if (!controller.value.isInitialized || controller.value.isTakingPicture) {
      return;
    }

    try {
      // 임시 저장 장소와 이름 생성
      Directory directory = await getTemporaryDirectory();
      final imgPath = '${directory.path}/${DateTime.now()}.jpeg';
      // 사진 촬영
      final XFile file = await controller.takePicture();
      await file.saveTo(imgPath);
      if (context.mounted) {
        context.pop(imgPath);
      }
    } catch (e) {
      // 사진 촬영 오류
      debugPrint('Error taking picture');
      if (context.mounted) showCameraErrorPopup(context);
    }
  }

  /// 플래시 on/off
  // 실제 기기에서 정상 작동하는지 확인 필요
  void toggleFlash() {
    if (isFlashOn) {
      controller.setFlashMode(FlashMode.off);
      isFlashOn = false;
    } else {
      controller.setFlashMode(FlashMode.always);
      isFlashOn = true;
    }

    notifyListeners();
  }

  /// 카메라 전환
  void changeCameraDirection() {
    if (controller.description.lensDirection == CameraLensDirection.back) {
      controller.setDescription(_cameras[1]);
    } else {
      controller.setDescription(_cameras[0]);
    }
  }

  /// 촬영 가이드
}

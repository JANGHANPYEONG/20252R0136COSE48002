import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/cam_shutter.dart';
import 'package:structure/components/camera_guide.dart';
import 'package:structure/components/loading_screen.dart';
import 'package:structure/viewModel/meat_registration/camera_view_model.dart';

class CameraScreen extends StatefulWidget {
  const CameraScreen({super.key});

  @override
  State<CameraScreen> createState() => _CameraScreenState();
}

class _CameraScreenState extends State<CameraScreen> {
  @override
  Widget build(BuildContext context) {
    CameraViewModel cameraViewModel = context.watch<CameraViewModel>();

    return Scaffold(
      backgroundColor: Colors.black,
      body: Stack(
        children: [
          // 카메라 화면
          cameraViewModel.isLoaded
              ? Positioned.fill(
                  child: CameraPreview(cameraViewModel.controller),
                )
              : const Center(child: LoadingScreen()),

          // 사진 가이드
          Align(
            alignment: Alignment.center,
            child: Container(
              width: 640.w,
              height: 640.w,
              padding: EdgeInsets.symmetric(horizontal: 40.w),
              child: const CameraGuide(color: Colors.white),
            ),
          ),

          // 상단 메뉴 버튼
          SafeArea(
            child: Padding(
              padding: EdgeInsets.only(top: 24.h),
              child: Align(
                alignment: Alignment.topCenter,
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    IconButton(
                      onPressed: () {
                        cameraViewModel.toggleFlash();
                      },
                      icon: Icon(
                        cameraViewModel.isFlashOn
                            ? Icons.flash_on_outlined
                            : Icons.flash_off_outlined,
                        size: 40.sp,
                        color: Colors.white,
                      ),
                    ),
                    IconButton(
                      onPressed: () {
                        cameraViewModel.changeCameraDirection();
                      },
                      icon: Icon(
                        Icons.cameraswitch_outlined,
                        size: 40.sp,
                        color: Colors.white,
                      ),
                    ),
                    IconButton(
                      onPressed: () {},
                      icon: Icon(
                        Icons.help_outline_outlined,
                        size: 40.sp,
                        color: Colors.white,
                      ),
                    ),
                    IconButton(
                      onPressed: () {
                        context.pop();
                      },
                      icon: Icon(
                        Icons.close,
                        size: 40.sp,
                        color: Colors.white,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),

          // 하단 촬영 버튼
          SafeArea(
            child: Align(
              alignment: Alignment.bottomCenter,
              child: Container(
                padding: EdgeInsets.only(bottom: 108.h),
                child: GestureDetector(
                  onTap: () {
                    // 사진 찍기 함수 호출
                    cameraViewModel.takePicture();
                  },
                  child: CamShutter(isReady: cameraViewModel.canTakePicture),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

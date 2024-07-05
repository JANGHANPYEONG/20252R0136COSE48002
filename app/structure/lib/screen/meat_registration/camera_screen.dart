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
    return Scaffold(
      backgroundColor: Colors.black,
      body: Stack(
        children: [
          // 카메라 화면
          context.watch<CameraViewModel>().isLoaded
              ? Positioned.fill(
                  child: CameraPreview(
                      context.watch<CameraViewModel>().controller),
                )
              : const Center(child: LoadingScreen()),

          // 사진 가이드
          Align(
            alignment: Alignment.center,
            child: SizedBox(
              width: 560.w,
              height: 620.h,
              child: const Positioned.fill(
                  child: CameraGuide(color: Colors.white)),
            ),
          ),

          // 상단 메뉴 버튼
          SafeArea(
            child: Padding(
              padding: EdgeInsets.fromLTRB(0, 16.h, 0, 0),
              child: Align(
                alignment: Alignment.topCenter,
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    IconButton(
                      onPressed: () {
                        context.read<CameraViewModel>().toggleFlash();
                      },
                      icon: Icon(
                        context.read<CameraViewModel>().isFlashOn
                            ? Icons.flash_on_outlined
                            : Icons.flash_off_outlined,
                        size: 42.sp,
                        color: Colors.black,
                      ),
                    ),
                    IconButton(
                      onPressed: () {
                        context.read<CameraViewModel>().changeCameraDirection();
                      },
                      icon: Icon(
                        Icons.cameraswitch_outlined,
                        size: 42.sp,
                        color: Colors.black,
                      ),
                    ),
                    IconButton(
                      onPressed: () {},
                      icon: Icon(
                        Icons.help_outline_outlined,
                        size: 42.sp,
                        color: Colors.black,
                      ),
                    ),
                    IconButton(
                      onPressed: () {
                        context.pop();
                      },
                      icon: Icon(
                        Icons.close,
                        size: 42.sp,
                        color: Colors.black,
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
                    context.read<CameraViewModel>().takePicture(context);
                  },
                  child: CamShutter(
                      isReady: context.read<CameraViewModel>().canTakePicture),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

//
//
// 관리번호 생성페이지 (view)
//
//

import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_text_button.dart';
import 'package:structure/components/main_button.dart';
import 'package:structure/config/palette.dart';
import 'package:structure/config/userfuls.dart';
import 'package:structure/screen/meat_registration/creation_management_num_loading_screen.dart';
import 'package:structure/viewModel/meat_registration/creation_management_num_view_model.dart.dart';

class CreationManagementNumScreen extends StatelessWidget {
  const CreationManagementNumScreen({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    CreationManagementNumViewModel creationManagementNumViewModel =
        context.watch<CreationManagementNumViewModel>();

    return Scaffold(
      body: Container(
        child: creationManagementNumViewModel.isLoading
            ? const CreationManagementNumLoadingScreen()
            : Container(
                margin: EdgeInsets.symmetric(horizontal: 40.w),
                child: Column(
                  children: [
                    SizedBox(
                      height: 550.h,
                      child: Stack(
                        children: [
                          // 성공 이미지
                          Center(
                            child: Transform.translate(
                              offset: Offset(0, 144.h),
                              child: Image.asset(
                                'assets/images/success.png',
                                width: 200.w,
                                height: 176.h,
                              ),
                            ),
                          ),

                          // 성공 텍스트
                          Container(
                            margin: EdgeInsets.only(top: 188.h),
                            child: Text('관리번호가\n생성되었습니다!', style: Palette.h2),
                          ),
                        ],
                      ),
                    ),

                    // 관리 번호
                    Container(
                      width: 448.w,
                      height: 108.h,
                      alignment: Alignment.center,
                      decoration: BoxDecoration(
                        color: Palette.onPrimaryContainer,
                        borderRadius: BorderRadius.circular(20.r),
                      ),
                      child: Text(
                        creationManagementNumViewModel.managementNum,
                        textAlign: TextAlign.center,
                        style: Palette.h1,
                      ),
                    ),
                    SizedBox(height: 32.h),

                    // 정보 컨테이너
                    Container(
                      width: double.infinity,
                      height: 224.h,
                      padding: EdgeInsets.all(40.w),
                      decoration: BoxDecoration(
                        border: Border.all(color: Palette.onPrimary),
                        borderRadius: BorderRadius.circular(20.r),
                      ),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                        children: [
                          Row(
                            children: [
                              // 기본 정보
                              Text('기본 정보', style: Palette.h5Secondary),
                              const Spacer(),
                              ClipOval(
                                child: Image.file(
                                  File(creationManagementNumViewModel
                                      .meatModel.sensoryEval!['imagePath']),
                                  width: 40.w,
                                  height: 40.h,
                                  fit: BoxFit.fill,
                                ),
                              ),
                              SizedBox(width: 16.w),
                              Text(
                                '${creationManagementNumViewModel.meatModel.speciesValue}•${creationManagementNumViewModel.meatModel.primalValue}•${creationManagementNumViewModel.meatModel.secondaryValue}',
                                style: Palette.h5,
                              )
                            ],
                          ),

                          // 이력 번호
                          Row(
                            children: [
                              Text('이력번호', style: Palette.h5Secondary),
                              const Spacer(),
                              Text(
                                '${creationManagementNumViewModel.meatModel.traceNum}',
                                style: Palette.h5,
                              )
                            ],
                          ),

                          // 날짜
                          Row(
                            children: [
                              Text('날짜', style: Palette.h5Secondary),
                              const Spacer(),
                              Text(
                                Usefuls.parseDate(Usefuls.getCurrentDate()),
                                style: Palette.h5,
                              )
                            ],
                          )
                        ],
                      ),
                    ),
                    const Spacer(),

                    // QR 버튼
                    MainButton(
                      width: double.infinity,
                      height: 96.h,
                      text: 'QR코드 출력하기',
                      onPressed: () async =>
                          creationManagementNumViewModel.clickedQR(),
                    ),
                    SizedBox(height: 16.h),

                    // 홈 이동 버튼
                    Container(
                      margin: EdgeInsets.only(bottom: 40.h),
                      child: CustomTextButton(
                        title: '홈으로 이동하기',
                        onPressed: () =>
                            creationManagementNumViewModel.clickedHomeButton(),
                      ),
                    ),
                  ],
                ),
              ),
      ),
    );
  }
}

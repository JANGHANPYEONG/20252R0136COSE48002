import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_text_button.dart';
import 'package:structure/components/main_button.dart';
import 'package:structure/config/pallete.dart';
import 'package:structure/config/userfuls.dart';
import 'package:structure/screen/meat_registration/creation_management_num_loading_screen.dart';
import 'package:structure/viewModel/meat_registration/creation_management_num_view_model.dart.dart';

class CreationManagementNumScreen extends StatelessWidget {
  const CreationManagementNumScreen({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Container(
        child: context.watch<CreationManagementNumViewModel>().isLoading
            ? const CreationManagementNumLoadingScreen()
            : Column(
                children: [
                  SizedBox(
                    height: 550.h,
                    child: Stack(
                      children: [
                        // 성공 이미지
                        Center(
                          child: Transform.translate(
                            offset: Offset(0, 150.h),
                            child: Image.asset(
                              'assets/images/success.png',
                              width: 202.w,
                              height: 180.h,
                            ),
                          ),
                        ),

                        // 성공 텍스트
                        Container(
                          margin: EdgeInsets.only(left: 46.w, top: 182.h),
                          child: Text('관리번호가\n생성되었습니다!', style: Palette.h2),
                        ),
                      ],
                    ),
                  ),

                  // 관리 번호
                  Container(
                    width: 456.w,
                    height: 141.h,
                    alignment: Alignment.center,
                    decoration: BoxDecoration(
                      color: Palette.fieldEmptyBg,
                      borderRadius: BorderRadius.circular(30.r),
                    ),
                    child: Text(
                      context
                          .read<CreationManagementNumViewModel>()
                          .managementNum,
                      textAlign: TextAlign.center,
                      style: Palette.h1,
                    ),
                  ),
                  SizedBox(height: 35.h),

                  // 정보 컨테이너
                  Container(
                    width: 640.w,
                    height: 251.h,
                    padding:
                        EdgeInsets.symmetric(horizontal: 44.w, vertical: 55.h),
                    decoration: BoxDecoration(
                      border: Border.all(color: Palette.fieldBorder),
                      borderRadius: BorderRadius.circular(20.r),
                    ),
                    child: Column(children: [
                      Row(
                        children: [
                          // 기본 정보
                          Text('기본 정보', style: Palette.h5Grey),
                          const Spacer(),
                          ClipOval(
                            child: Image.file(
                              File(context
                                  .read<CreationManagementNumViewModel>()
                                  .meatModel
                                  .imagePath!),
                              width: 44.w,
                              height: 44.h,
                              fit: BoxFit.fill,
                            ),
                          ),
                          SizedBox(width: 25.w),
                          Text(
                            '${context.read<CreationManagementNumViewModel>().meatModel.speciesValue}•${context.read<CreationManagementNumViewModel>().meatModel.primalValue}•${context.read<CreationManagementNumViewModel>().meatModel.secondaryValue}',
                            style: Palette.h5,
                          )
                        ],
                      ),
                      const Spacer(),

                      // 이력 번호
                      Row(children: [
                        Text('이력번호', style: Palette.h5Grey),
                        const Spacer(),
                        Text(
                          "${context.read<CreationManagementNumViewModel>().meatModel.traceNum}",
                          style: Palette.h5,
                        )
                      ]),
                      const Spacer(),

                      // 날짜
                      Row(
                        children: [
                          Text('날짜', style: Palette.h5Grey),
                          const Spacer(),
                          Text(
                            Usefuls.parseDate(context
                                .read<CreationManagementNumViewModel>()
                                .meatModel
                                .createdAt),
                            style: Palette.h5,
                          )
                        ],
                      )
                    ]),
                  ),
                  const Spacer(),

                  // QR 버튼
                  Container(
                    margin: EdgeInsets.only(bottom: 20.h),
                    child: MainButton(
                      onPressed: () async => await context
                          .read<CreationManagementNumViewModel>()
                          .printQr(),
                      text: 'QR코드 출력하기',
                      width: 640.w,
                      height: 96.h,
                      mode: 1,
                    ),
                  ),

                  // 홈 이동 버튼
                  Container(
                    margin: EdgeInsets.only(bottom: 32.h),
                    child: CustomTextButton(
                      title: '홈으로 이동하기',
                      onPressed: () => context
                          .read<CreationManagementNumViewModel>()
                          .clickedHomeButton(context),
                    ),
                  ),
                ],
              ),
      ),
    );
  }
}

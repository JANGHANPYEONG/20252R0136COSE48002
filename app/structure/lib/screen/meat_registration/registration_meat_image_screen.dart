//
//
// 육류 이미지 페이지(View)
//
//

import 'dart:io';

import 'package:dotted_border/dotted_border.dart';
import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/loading_screen.dart';
import 'package:structure/components/main_button.dart';
import 'package:structure/config/pallete.dart';
import 'package:structure/viewModel/meat_registration/registration_meat_image_view_model.dart';

class RegistrationMeatImageScreen extends StatelessWidget {
  const RegistrationMeatImageScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: const CustomAppBar(
        title: '육류 단면 촬영',
        backButton: true,
        closeButton: false,
      ),
      body: Stack(
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              SizedBox(height: 30.h),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // 촬영 날짜
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('촬영 날짜', style: Palette.h4),
                      SizedBox(height: 20.h),
                      Container(
                        width: 315.w,
                        height: 78.h,
                        decoration: BoxDecoration(
                          color: Palette.fieldEmptyBg,
                          borderRadius: BorderRadius.circular(20.w),
                        ),
                        alignment: Alignment.centerLeft,
                        child: Padding(
                          padding: const EdgeInsets.only(left: 10.0),
                          child: Text(
                            context
                                .watch<RegistrationMeatImageViewModel>()
                                .date,
                            style: Palette.h4,
                          ),
                        ),
                      ),
                    ],
                  ),
                  SizedBox(width: 10.w),

                  // 촬영자
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('촬영자', style: Palette.h4),
                      SizedBox(height: 20.h),
                      Container(
                        width: 315.w,
                        height: 78.h,
                        decoration: BoxDecoration(
                          color: Palette.fieldEmptyBg,
                          borderRadius: BorderRadius.circular(20.w),
                        ),
                        alignment: Alignment.centerLeft,
                        child: Padding(
                          padding: const EdgeInsets.only(left: 10.0),
                          child: Text(
                            context
                                .watch<RegistrationMeatImageViewModel>()
                                .userName,
                            style: Palette.h4,
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
              SizedBox(height: 30.h),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('단면 촬영 사진', style: Palette.h4),
                  SizedBox(height: 20.h),
                  // 촬영 사진
                  context.watch<RegistrationMeatImageViewModel>().imagePath !=
                          null
                      ? Stack(
                          // 삭제 버튼을 이미지 위에 띄우기 위한 'stack' 위젯 사용
                          children: [
                            SizedBox(
                              width: 640.w,
                              height: 653.h,

                              // 이미지 할당
                              child: context
                                              .watch<
                                                  RegistrationMeatImageViewModel>()
                                              .imagePath !=
                                          null &&
                                      context
                                          .watch<
                                              RegistrationMeatImageViewModel>()
                                          .imagePath!
                                          .contains('http')
                                  ? Image.network(
                                      context
                                          .read<
                                              RegistrationMeatImageViewModel>()
                                          .imagePath!,
                                      loadingBuilder: (BuildContext context,
                                          Widget child,
                                          ImageChunkEvent? loadingProgress) {
                                        if (loadingProgress == null) {
                                          return child;
                                        } else {
                                          return LoadingScreen(
                                            value: loadingProgress
                                                        .expectedTotalBytes !=
                                                    null
                                                ? loadingProgress
                                                        .cumulativeBytesLoaded /
                                                    (loadingProgress
                                                            .expectedTotalBytes ??
                                                        1)
                                                : null,
                                          );
                                        }
                                      },
                                      errorBuilder: (BuildContext context,
                                          Object error,
                                          StackTrace? stackTrace) {
                                        return const Icon(Icons.error);
                                      },
                                    )
                                  : Image.file(
                                      File(context
                                          .read<
                                              RegistrationMeatImageViewModel>()
                                          .imagePath!),
                                      fit: BoxFit.cover,
                                    ),
                            ),

                            // 삭제 버튼
                            Positioned(
                              right: 15.h,
                              top: 15.h,
                              child: Container(
                                decoration: BoxDecoration(
                                  borderRadius: BorderRadius.circular(20.h),
                                  color: Colors.black,
                                ),
                                child: IconButton(
                                    onPressed: () => context
                                        .read<RegistrationMeatImageViewModel>()
                                        .deleteImage(context),
                                    iconSize: 55.h,
                                    icon: const Icon(
                                      Icons.delete_outline_outlined,
                                      color: Colors.white,
                                    )),
                              ),
                            )
                          ],
                        )

                      // 이미지 삽입 버튼
                      : InkWell(
                          onTap: () => context
                              .read<RegistrationMeatImageViewModel>()
                              .pickImage(context),
                          child: DottedBorder(
                            radius: Radius.circular(20.sp),
                            borderType: BorderType.RRect,
                            color: Palette.notEditableBg,
                            strokeWidth: 2.sp,
                            dashPattern: [10.w, 10.w],
                            child: SizedBox(
                              width: 640.w,
                              height: 653.h,
                              child: Image.asset(
                                'assets/images/add_circle.png',
                                cacheWidth: 50,
                                cacheHeight: 50,
                              ),
                            ),
                          ),
                        ),
                ],
              ),
              const Spacer(),

              // 저장 버튼
              Container(
                margin: EdgeInsets.only(bottom: 40.h),
                child: MainButton(
                  onPressed: context
                              .watch<RegistrationMeatImageViewModel>()
                              .imagePath !=
                          null
                      ? () async => await context
                          .read<RegistrationMeatImageViewModel>()
                          .saveMeatData(context)
                      : null,
                  text: context
                              .read<RegistrationMeatImageViewModel>()
                              .meatModel
                              .id ==
                          null
                      ? '완료'
                      : "수정사항 저장",
                  width: 640.w,
                  height: 96.h,
                  mode: 1,
                ),
              ),
            ],
          ),
          // 로딩 화면
          context.watch<RegistrationMeatImageViewModel>().isLoading
              ? const Center(child: LoadingScreen())
              : Container(),
        ],
      ),
    );
  }
}

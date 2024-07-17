//
//
// 육류 이미지 등록 페이지(수정 불가!) : Normal
//
//

import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/image_card.dart';
import 'package:structure/components/loading_screen.dart';
import 'package:structure/config/pallete.dart';
import 'package:structure/viewModel/data_management/normal/not_editable/insertion_meat_image_not_editable_view_model.dart';

class InsertionMeatImageNotEditableScreen extends StatelessWidget {
  const InsertionMeatImageNotEditableScreen({super.key});

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
                        height: 88.h,
                        decoration: BoxDecoration(
                          color: Palette.fieldEmptyBg,
                          borderRadius: BorderRadius.circular(15.r),
                        ),
                        alignment: Alignment.centerLeft,
                        child: Padding(
                          padding: EdgeInsets.only(left: 20.w),
                          child: Text(
                            context
                                .watch<InsertionMeatImageNotEditableViewModel>()
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
                        height: 88.h,
                        decoration: BoxDecoration(
                          color: Palette.fieldEmptyBg,
                          borderRadius: BorderRadius.circular(15.r),
                        ),
                        alignment: Alignment.centerLeft,
                        child: Padding(
                          padding: EdgeInsets.only(left: 20.w),
                          child: Text(
                            context
                                .watch<InsertionMeatImageNotEditableViewModel>()
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

              // 사진
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('단면 촬영 사진', style: Palette.h4),
                  SizedBox(height: 20.h),

                  // 촬영 사진
                  // SizedBox(
                  //   width: 640.w,
                  //   height: 653.h,
                  //   child: Image.network(
                  //     context
                  //         .read<InsertionMeatImageNotEditableViewModel>()
                  //         .imagePath!,
                  //     loadingBuilder: (BuildContext context, Widget child,
                  //         ImageChunkEvent? loadingProgress) {
                  //       if (loadingProgress == null) {
                  //         return child;
                  //       } else {
                  //         return LoadingScreen(
                  //           value: loadingProgress.expectedTotalBytes != null
                  //               ? loadingProgress.cumulativeBytesLoaded /
                  //                   (loadingProgress.expectedTotalBytes ?? 1)
                  //               : null,
                  //         );
                  //       }
                  //     },
                  //     errorBuilder: (BuildContext context, Object error,
                  //         StackTrace? stackTrace) {
                  //       return const Icon(Icons.error);
                  //     },
                  //     fit: BoxFit.cover,
                  //   ),
                  // ),

                  ImageCard(
                    imagePath: context
                                .read<InsertionMeatImageNotEditableViewModel>()
                                .imagePath ==
                            null
                        ? '없음'
                        : context
                            .read<InsertionMeatImageNotEditableViewModel>()
                            .imagePath!,
                    // '없음',
                  ),
                ],
              ),
            ],
          ),
          context.watch<InsertionMeatImageNotEditableViewModel>().isLoading
              ? const Center(
                  child: LoadingScreen(),
                )
              : Container(),
        ],
      ),
    );
  }
}

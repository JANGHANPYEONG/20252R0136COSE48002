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
import 'package:structure/config/pallete.dart';
import 'package:structure/viewModel/data_management/normal/not_editable/insertion_meat_image_not_editable_view_model.dart';

class InsertionMeatImageNotEditableScreen extends StatelessWidget {
  const InsertionMeatImageNotEditableScreen({super.key});

  @override
  Widget build(BuildContext context) {
    InsertionMeatImageNotEditableViewModel
        insertionMeatImageNotEditableViewModel =
        context.watch<InsertionMeatImageNotEditableViewModel>();

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: const CustomAppBar(
        title: '원육 단면 촬영',
        backButton: true,
        closeButton: false,
      ),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        mainAxisSize: MainAxisSize.min,
        children: [
          SizedBox(height: 24.h),

          Container(
            margin: EdgeInsets.symmetric(horizontal: 40.w),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              mainAxisSize: MainAxisSize.min,
              children: [
                // 촬영 날짜
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('촬영 날짜', style: Pallete.h4),
                    SizedBox(height: 16.h),
                    Container(
                      width: 316.w,
                      height: 88.h,
                      decoration: BoxDecoration(
                        color: Pallete.fieldEmptyBg,
                        borderRadius: BorderRadius.circular(20.r),
                      ),
                      alignment: Alignment.centerLeft,
                      child: Padding(
                        padding: EdgeInsets.only(left: 16.w),
                        child: Text(
                          insertionMeatImageNotEditableViewModel.date,
                          style: Pallete.h4,
                        ),
                      ),
                    ),
                  ],
                ),
                SizedBox(width: 8.w),

                // 촬영자
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('촬영자', style: Pallete.h4),
                    SizedBox(height: 16.h),
                    Container(
                      width: 316.w,
                      height: 88.h,
                      decoration: BoxDecoration(
                        color: Pallete.fieldEmptyBg,
                        borderRadius: BorderRadius.circular(20.r),
                      ),
                      alignment: Alignment.centerLeft,
                      child: Padding(
                        padding: EdgeInsets.only(left: 16.w),
                        child: Text(
                          insertionMeatImageNotEditableViewModel.userName,
                          style: Pallete.h4,
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          SizedBox(height: 32.h),

          // 단면 사진 촬영 텍스트
          Container(
            alignment: Alignment.centerLeft,
            margin: EdgeInsets.symmetric(horizontal: 40.w),
            child: Text('단면 촬영 사진', style: Pallete.h4),
          ),
          SizedBox(height: 16.h),

          // 이미지
          ImageCard(
            imagePath: insertionMeatImageNotEditableViewModel.imagePath,
          ),
        ],
      ),
    );
  }
}

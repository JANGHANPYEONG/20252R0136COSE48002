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
                        insertionMeatImageNotEditableViewModel.date,
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
                        insertionMeatImageNotEditableViewModel.userName,
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

              // 이미지
              ImageCard(
                imagePath:
                    insertionMeatImageNotEditableViewModel.imagePath == null
                        ? '없음'
                        : insertionMeatImageNotEditableViewModel.imagePath!,
              ),
            ],
          ),
        ],
      ),
    );
  }
}

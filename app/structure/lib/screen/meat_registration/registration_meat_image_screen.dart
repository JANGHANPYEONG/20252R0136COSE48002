//
//
// 육류 이미지 페이지(View)
//
//

import 'package:dotted_border/dotted_border.dart';
import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/image_card.dart';
import 'package:structure/components/loading_screen.dart';
import 'package:structure/components/main_button.dart';
import 'package:structure/config/pallete.dart';
import 'package:structure/viewModel/meat_registration/insertion_meat_image_view_model.dart';

class RegistrationMeatImageScreen extends StatelessWidget {
  const RegistrationMeatImageScreen({super.key});

  @override
  Widget build(BuildContext context) {
    InsertionMeatImageViewModel insertionMeatImageViewModel =
        context.watch<InsertionMeatImageViewModel>();

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: CustomAppBar(
        title: insertionMeatImageViewModel.title,
        backButton: true,
        closeButton: false,
        backButtonOnPressed:
            insertionMeatImageViewModel.backBtnPressed(context),
      ),
      body: Stack(
        children: [
          Column(
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
                        Text('촬영 날짜', style: Palette.h4),
                        SizedBox(height: 16.h),
                        Container(
                          width: 316.w,
                          height: 88.h,
                          decoration: BoxDecoration(
                            color: Palette.fieldEmptyBg,
                            borderRadius: BorderRadius.circular(20.r),
                          ),
                          alignment: Alignment.centerLeft,
                          child: Padding(
                            padding: EdgeInsets.only(left: 16.w),
                            child: Text(
                              insertionMeatImageViewModel.date,
                              style: Palette.h4,
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
                        Text('촬영자', style: Palette.h4),
                        SizedBox(height: 16.h),
                        Container(
                          width: 316.w,
                          height: 88.h,
                          decoration: BoxDecoration(
                            color: Palette.fieldEmptyBg,
                            borderRadius: BorderRadius.circular(20.r),
                          ),
                          alignment: Alignment.centerLeft,
                          child: Padding(
                            padding: EdgeInsets.only(left: 16.w),
                            child: Text(
                              insertionMeatImageViewModel.userName,
                              style: Palette.h4,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              SizedBox(height: 32.h),

              Container(
                alignment: Alignment.centerLeft,
                margin: EdgeInsets.symmetric(horizontal: 40.w),
                child: Text('단면 촬영 사진', style: Palette.h4),
              ),
              SizedBox(height: 16.h),

              // 사진
              insertionMeatImageViewModel.imgPath != null
                  // 등록된 이미지가 있음
                  ? Stack(
                      alignment: Alignment.topRight,
                      // 삭제 버튼을 이미지 위에 띄우기 위한 'stack' 위젯 사용
                      children: [
                        ImageCard(
                          imagePath: insertionMeatImageViewModel.imgPath,
                        ),
                        // 삭제 버튼
                        Positioned(
                          right: 56.w,
                          top: 16.h,
                          child: Container(
                            decoration: BoxDecoration(
                              borderRadius: BorderRadius.circular(20.r),
                              color: Colors.black,
                            ),
                            child: IconButton(
                              onPressed: () => insertionMeatImageViewModel
                                  .deleteImage(context),
                              iconSize: 56.w,
                              icon: const Icon(
                                Icons.delete_outline_outlined,
                                color: Colors.white,
                              ),
                            ),
                          ),
                        )
                      ],
                    )
                  // 등록된 이미지가 없음 (사진 촬영)
                  // 이미지 삽입 버튼
                  : SizedBox(
                      width: 640.w,
                      height: 640.w,
                      child: InkWell(
                        borderRadius: BorderRadius.circular(20.r),
                        onTap: () =>
                            insertionMeatImageViewModel.pickImage(context),
                        child: DottedBorder(
                          radius: Radius.circular(20.r),
                          borderType: BorderType.RRect,
                          color: Palette.notEditableBg,
                          strokeWidth: 2.sp,
                          dashPattern: [12.w, 12.w],
                          child: Center(
                            child: Image.asset(
                              'assets/images/add_circle.png',
                              cacheWidth: 48,
                              cacheHeight: 48,
                            ),
                          ),
                        ),
                      ),
                    ),
              const Spacer(),

              // 저장 버튼
              Container(
                margin: EdgeInsets.fromLTRB(40.w, 0, 40.w, 40.w),
                child: MainButton(
                  onPressed: insertionMeatImageViewModel.imgPath != null
                      ? () async {
                          await insertionMeatImageViewModel
                              .saveMeatData(context);
                        }
                      : null,
                  text: insertionMeatImageViewModel.saveBtnText,
                  width: double.infinity,
                  height: 96.h,
                  mode: 1,
                ),
              ),
            ],
          ),

          // 로딩 화면
          insertionMeatImageViewModel.isLoading
              ? const Center(child: LoadingScreen())
              : Container(),
        ],
      ),
    );
  }
}

//
//
// 육류 이미지 등록 페이지(수정 불가!) : Normal
//
//

import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/loading_screen.dart';
import 'package:structure/components/main_button.dart';
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
              SizedBox(
                height: 30.h,
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('촬영 날짜', style: Palette.h4),
                      SizedBox(
                        height: 20.h,
                      ),
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
                                .watch<InsertionMeatImageNotEditableViewModel>()
                                .date,
                            style: Palette.h4,
                          ),
                        ),
                      ),
                    ],
                  ),
                  SizedBox(width: 10.w),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('촬영자', style: Palette.h4),
                      SizedBox(
                        height: 20.h,
                      ),
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
                                .watch<InsertionMeatImageNotEditableViewModel>()
                                .userName,
                            style: Palette.h5,
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
              SizedBox(
                height: 30.h,
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('단면 촬영 사진', style: Palette.h4),
                  SizedBox(
                    height: 20.h,
                  ),
                  SizedBox(
                    width: 640.w,
                    height: 653.h,
                    child: Image.network(
                      context
                          .read<InsertionMeatImageNotEditableViewModel>()
                          .imagePath!,
                      loadingBuilder: (BuildContext context, Widget child,
                          ImageChunkEvent? loadingProgress) {
                        if (loadingProgress == null) {
                          return child;
                        } else {
                          return LoadingScreen(
                            value: loadingProgress.expectedTotalBytes != null
                                ? loadingProgress.cumulativeBytesLoaded /
                                    (loadingProgress.expectedTotalBytes ?? 1)
                                : null,
                          );
                        }
                      },
                      errorBuilder: (BuildContext context, Object error,
                          StackTrace? stackTrace) {
                        return const Icon(Icons.error);
                      },
                    ),
                  ),
                ],
              ),
              const Spacer(),
              Container(
                margin: EdgeInsets.only(bottom: 40.h),
                child: MainButton(
                  onPressed: () {
                    context
                        .read<InsertionMeatImageNotEditableViewModel>()
                        .clickedNextButton(context);
                  },
                  text: '완료',
                  width: 640.w,
                  height: 96.h,
                  mode: 1,
                ),
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

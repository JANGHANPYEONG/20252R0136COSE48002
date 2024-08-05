//
//
// 육류 분류 페이지(수정 불가!) : Normal
//
//

import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/custom_drop_down.dart';
import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:structure/config/palette.dart';
import 'package:structure/viewModel/data_management/normal/not_editable/insertion_meat_info_not_editable_view_model.dart';

class MeatInfoNotEditableScreen extends StatefulWidget {
  const MeatInfoNotEditableScreen({super.key});

  @override
  State<MeatInfoNotEditableScreen> createState() =>
      _MeatInfoNotEditableScreenState();
}

class _MeatInfoNotEditableScreenState extends State<MeatInfoNotEditableScreen> {
  @override
  Widget build(BuildContext context) {
    InsertionMeatInfoNotEditableViewModel meatInfoNotEditableViewModel =
        context.watch<InsertionMeatInfoNotEditableViewModel>();

    return GestureDetector(
      onTap: () => FocusScope.of(context).unfocus(),
      child: Scaffold(
        appBar: const CustomAppBar(
          title: '육류 기본정보',
          backButton: true,
          closeButton: false,
        ),
        resizeToAvoidBottomInset: false,
        body: Container(
          margin: EdgeInsets.symmetric(horizontal: 40.w),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              SizedBox(height: 24.h),

              // 종류
              Text('종류', style: Palette.h4),
              SizedBox(height: 16.h),

              Row(
                children: [
                  // 소
                  Container(
                    width: 120.w,
                    height: 72.h,
                    decoration: BoxDecoration(
                      color: meatInfoNotEditableViewModel.speciesCheck()
                          ? Palette.onPrimaryContainer
                          : Palette.onSecondary,
                      borderRadius: BorderRadius.all(Radius.circular(50.r)),
                    ),
                    child: Center(
                      child: Text(
                        "소",
                        textAlign: TextAlign.center,
                        style: Palette.h4.copyWith(
                          color: meatInfoNotEditableViewModel.speciesCheck()
                              ? Palette.onSecondary
                              : Palette.onPrimaryContainer,
                        ),
                      ),
                    ),
                  ),
                  SizedBox(width: 16.w),

                  // 돼지
                  Container(
                    width: 120.w,
                    height: 72.h,
                    decoration: BoxDecoration(
                      color: meatInfoNotEditableViewModel.speciesCheck()
                          ? Palette.onSecondary
                          : Palette.onPrimaryContainer,
                      borderRadius: BorderRadius.all(Radius.circular(50.r)),
                    ),
                    child: Center(
                      child: Text(
                        "돼지",
                        textAlign: TextAlign.center,
                        style: Palette.h4.copyWith(
                          color: meatInfoNotEditableViewModel.speciesCheck()
                              ? Palette.onPrimaryContainer
                              : Palette.onSecondary,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
              SizedBox(height: 32.h),

              Text('부위', style: Palette.h4),
              SizedBox(height: 16.h),

              // 대분류
              CustomDropdown(
                hintText: Text(
                  meatInfoNotEditableViewModel.primalValue,
                  style: Palette.h4,
                ),
                value: null,
                itemList: const [],
                onChanged: null,
                hasDropdown: false,
              ),
              SizedBox(height: 16.h),

              // 소분류
              CustomDropdown(
                hintText: Text(
                  meatInfoNotEditableViewModel.secondaryValue,
                  style: Palette.h4,
                ),
                value: null,
                itemList: const [],
                onChanged: null,
                hasDropdown: false,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

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
import 'package:structure/config/pallete.dart';
import 'package:structure/viewModel/data_management/normal/not_editable/insertion_meat_info_not_editable_view_model.dart';

class InsertionMeatInfoNotEditableScreen extends StatefulWidget {
  const InsertionMeatInfoNotEditableScreen({super.key});

  @override
  State<InsertionMeatInfoNotEditableScreen> createState() =>
      _InsertionMeatInfoNotEditableScreenState();
}

class _InsertionMeatInfoNotEditableScreenState
    extends State<InsertionMeatInfoNotEditableScreen> {
  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => FocusScope.of(context).unfocus(),
      child: Scaffold(
        backgroundColor: Colors.white,
        resizeToAvoidBottomInset: false,
        appBar: const CustomAppBar(
          title: '육류 기본정보',
          backButton: true,
          closeButton: false,
        ),
        body: Column(
          children: [
            Container(
              margin: EdgeInsets.symmetric(horizontal: 40.w),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  SizedBox(height: 56.h),
                  Text('종류', style: Palette.h4),
                  SizedBox(height: 12.h),
                  Row(
                    children: [
                      // 소
                      Container(
                        width: 116.w,
                        height: 72.h,
                        decoration: BoxDecoration(
                          color: context
                                  .read<InsertionMeatInfoNotEditableViewModel>()
                                  .speciesCheck()
                              ? Palette.basicSpeciesColor
                              : Palette.checkSpeciesNotEditableColor,
                          borderRadius: BorderRadius.all(Radius.circular(50.r)),
                        ),
                        child: Center(
                          child: Text(
                            "소",
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              fontSize: 30.sp,
                              fontWeight: FontWeight.w700,
                              color: context
                                      .read<
                                          InsertionMeatInfoNotEditableViewModel>()
                                      .speciesCheck()
                                  ? Palette.basicSpeciesTextColor
                                  : Palette.checkSpeciesTextColor,
                            ),
                          ),
                        ),
                      ),
                      SizedBox(width: 16.w),

                      // 돼지
                      Container(
                        width: 116.w,
                        height: 72.h,
                        decoration: BoxDecoration(
                          color: context
                                  .read<InsertionMeatInfoNotEditableViewModel>()
                                  .speciesCheck()
                              ? Palette.checkSpeciesNotEditableColor
                              : Palette.basicSpeciesColor,
                          borderRadius: BorderRadius.all(Radius.circular(50.r)),
                        ),
                        child: Center(
                          child: Text(
                            "돼지",
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              fontSize: 30.sp,
                              fontWeight: FontWeight.w700,
                              color: context
                                      .read<
                                          InsertionMeatInfoNotEditableViewModel>()
                                      .speciesCheck()
                                  ? Palette.checkSpeciesTextColor
                                  : Palette.basicSpeciesTextColor,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                  SizedBox(height: 30.h),

                  Text('부위', style: Palette.h4),
                  SizedBox(height: 12.h),

                  // 대분류
                  CustomDropdown(
                    hintText: Text(
                        context
                            .read<InsertionMeatInfoNotEditableViewModel>()
                            .primalValue,
                        style: Palette.h4),
                    value: null,
                    itemList: const [],
                    onChanged: null,
                    hasDropdown: false,
                  ),
                  SizedBox(height: 16.h),

                  // 소분류
                  CustomDropdown(
                    hintText: Text(
                        context
                            .read<InsertionMeatInfoNotEditableViewModel>()
                            .secondaryValue,
                        style: Palette.h4),
                    value: null,
                    itemList: const [],
                    onChanged: null,
                    hasDropdown: false,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

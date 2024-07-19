//
//
// 육류 기본정보 부위 추가(View)
//
//

import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/custom_drop_down.dart';
import 'package:structure/components/main_button.dart';

import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:structure/config/pallete.dart';
import 'package:structure/viewModel/meat_registration/insertion_meat_info_view_model.dart';

class InsertionMeatInfoScreen extends StatefulWidget {
  const InsertionMeatInfoScreen({super.key});

  @override
  State<InsertionMeatInfoScreen> createState() =>
      _InsertionMeatInfoScreenState();
}

class _InsertionMeatInfoScreenState extends State<InsertionMeatInfoScreen> {
  @override
  Widget build(BuildContext context) {
    InsertionMeatInfoViewModel insertionMeatInfoViewModel =
        context.watch<InsertionMeatInfoViewModel>();

    return GestureDetector(
      onTap: () => FocusScope.of(context).unfocus(),
      child: Scaffold(
        backgroundColor: Colors.white,
        resizeToAvoidBottomInset: false,
        appBar: CustomAppBar(
            title: '육류 기본정보',
            backButton: true,
            closeButton: false,
            backButtonOnPressed:
                insertionMeatInfoViewModel.backBtnPressed(context)),
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
                          color: insertionMeatInfoViewModel.speciesCheckFunc()
                              ? Palette.basicSpeciesColor
                              : Palette.checkSpeciesColor,
                          borderRadius: BorderRadius.all(Radius.circular(50.r)),
                        ),
                        child: Center(
                          child: Text(
                            "소",
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              fontSize: 30.sp,
                              fontWeight: FontWeight.w700,
                              color:
                                  insertionMeatInfoViewModel.speciesCheckFunc()
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
                          color: insertionMeatInfoViewModel.speciesCheckFunc()
                              ? Palette.checkSpeciesColor
                              : Palette.basicSpeciesColor,
                          borderRadius: BorderRadius.circular(35.r),
                        ),
                        child: Center(
                          child: Text(
                            "돼지",
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              fontSize: 30.sp,
                              fontWeight: FontWeight.w700,
                              color:
                                  insertionMeatInfoViewModel.speciesCheckFunc()
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

                  // 'CustomDropdown' 컴포넌트를 사용하여 분류 지정
                  // 대분류
                  CustomDropdown(
                    hintText: Text('대분할', style: Palette.dropDownTitleStyle),
                    value: insertionMeatInfoViewModel.primalValue,
                    itemList: insertionMeatInfoViewModel.largeDiv,
                    onChanged: insertionMeatInfoViewModel.isSelectedSpecies
                        ? (value) {
                            insertionMeatInfoViewModel.primalValue =
                                value as String;
                            insertionMeatInfoViewModel.setPrimal();
                          }
                        : null,
                  ),
                  SizedBox(height: 16.h),

                  // 'CustomDropdown' 컴포넌트를 사용하여 분류 지정
                  // 소분류
                  CustomDropdown(
                    hintText: Text('소분할', style: Palette.dropDownTitleStyle),
                    value: insertionMeatInfoViewModel.secondaryValue,
                    itemList: insertionMeatInfoViewModel.litteDiv,
                    onChanged: insertionMeatInfoViewModel.isSelectedPrimal
                        ? (value) {
                            insertionMeatInfoViewModel.secondaryValue =
                                value as String;
                            insertionMeatInfoViewModel.setSecondary();
                          }
                        : null,
                  ),
                ],
              ),
            ),
            const Spacer(),
            // 완료 버튼
            Container(
              margin: EdgeInsets.only(bottom: 28.h),
              child: MainButton(
                onPressed: insertionMeatInfoViewModel.completed
                    ? () {
                        insertionMeatInfoViewModel.clickedNextButton(context);
                      }
                    : null,
                text: insertionMeatInfoViewModel.meatModel.meatId == null
                    ? '완료'
                    : '수정사항 저장',
                width: 658.w,
                height: 104.h,
                mode: 1,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

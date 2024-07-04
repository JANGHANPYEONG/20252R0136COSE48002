//
//
// 육류 분류 페이지(View)
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
  void initState() {
    super.initState();

    context.read<InsertionMeatInfoViewModel>().initialize();
  }

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
              margin: EdgeInsets.symmetric(horizontal: 50.w),
              child: Column(
                children: [
                  SizedBox(
                    height: 70.h,
                  ),
                  Row(
                    children: [
                      Text('종류', style: Palette.h4),
                    ],
                  ),
                  SizedBox(
                    height: 20.h,
                  ),
                  Row(
                    children: [
                      Container(
                        decoration: BoxDecoration(
                          color: context
                                  .watch<InsertionMeatInfoViewModel>()
                                  .speciesCheckFunc()
                              ? Palette.basicSpeciesColor
                              : Palette.checkSpeciesColor,
                          borderRadius: const BorderRadius.all(
                            Radius.circular(35.0),
                          ),
                        ),
                        child: Column(
                          children: [
                            const SizedBox(
                              height: 13,
                            ),
                            SizedBox(
                              width: 80,
                              height: 40,
                              child: Text(
                                "소",
                                textAlign: TextAlign.center,
                                style: TextStyle(
                                  fontSize: 18.0,
                                  fontWeight: FontWeight.w700,
                                  color: context
                                          .watch<InsertionMeatInfoViewModel>()
                                          .speciesCheckFunc()
                                      ? Palette.basicSpeciesTextColor
                                      : Palette.checkSpeciesTextColor,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(
                        width: 10,
                      ),
                      Container(
                        decoration: BoxDecoration(
                          color: context
                                  .watch<InsertionMeatInfoViewModel>()
                                  .speciesCheckFunc()
                              ? Palette.checkSpeciesColor
                              : Palette.basicSpeciesColor,
                          borderRadius: const BorderRadius.all(
                            Radius.circular(35.0),
                          ),
                        ),
                        child: Column(
                          children: [
                            const SizedBox(
                              height: 14,
                            ),
                            SizedBox(
                              width: 80,
                              height: 40,
                              child: Text(
                                "돼지",
                                textAlign: TextAlign.center,
                                style: TextStyle(
                                  fontSize: 18.0,
                                  fontWeight: FontWeight.w700,
                                  color: context
                                          .watch<InsertionMeatInfoViewModel>()
                                          .speciesCheckFunc()
                                      ? Palette.checkSpeciesTextColor
                                      : Palette.basicSpeciesTextColor,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  SizedBox(
                    height: 42.0.h,
                  ),
                  Row(
                    children: [
                      Text('부위', style: Palette.h4),
                    ],
                  ),
                  SizedBox(
                    height: 20.h,
                  ),
                  // 'CustomDropdown' 컴포넌트를 사용하여 분류 지정
                  CustomDropdown(
                    hintText: Text('대분할', style: Palette.dropDownTitleStyle),
                    value:
                        context.watch<InsertionMeatInfoViewModel>().primalValue,
                    itemList:
                        context.read<InsertionMeatInfoViewModel>().largeDiv,
                    onChanged: context
                            .watch<InsertionMeatInfoViewModel>()
                            .isSelectedSpecies
                        ? (value) {
                            context
                                .read<InsertionMeatInfoViewModel>()
                                .primalValue = value as String;
                            context
                                .read<InsertionMeatInfoViewModel>()
                                .setPrimal();
                          }
                        : null,
                  ),
                  SizedBox(
                    height: 16.h,
                  ),
                  // 'CustomDropdown' 컴포넌트를 사용하여 분류 지정
                  CustomDropdown(
                    hintText: Text('소분할', style: Palette.dropDownTitleStyle),
                    value: context
                        .watch<InsertionMeatInfoViewModel>()
                        .secondaryValue,
                    itemList:
                        context.watch<InsertionMeatInfoViewModel>().litteDiv,
                    onChanged: context
                            .watch<InsertionMeatInfoViewModel>()
                            .isSelectedPrimal
                        ? (value) {
                            context
                                .read<InsertionMeatInfoViewModel>()
                                .secondaryValue = value as String;
                            context
                                .read<InsertionMeatInfoViewModel>()
                                .setSecondary();
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
                onPressed: context.watch<InsertionMeatInfoViewModel>().completed
                    ? () => context
                        .read<InsertionMeatInfoViewModel>()
                        .clickedNextButton(context)
                    : null,
                text: context.read<InsertionMeatInfoViewModel>().meatModel.id ==
                        null
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

//
//
// 가열육 추가 데이터 입력 (3일차, 7일차, 14일차) : Researcher
//
//

import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/data_title.dart';
import 'package:structure/components/part_eval.dart';
import 'package:structure/config/palette.dart';
import 'package:structure/viewModel/data_management/researcher/insertion_heated_sensory_tenderness_view_model.dart';

class InsertionHeatedSensoryTendernessScreen extends StatefulWidget {
  const InsertionHeatedSensoryTendernessScreen({super.key});

  @override
  State<InsertionHeatedSensoryTendernessScreen> createState() =>
      _InsertionHeatedSensoryTendernessScreenState();
}

class _InsertionHeatedSensoryTendernessScreenState
    extends State<InsertionHeatedSensoryTendernessScreen> {
  List<String> text = ['Tenderness', '연도', '질김', '', '보통', '', '연함'];
  List<String> period = ['3일차', '7일차', '14일차', '21일차'];

  @override
  Widget build(BuildContext context) {
    InsertionHeatedSensoryTendernessViewModel
        insertionHeatedSensoryTendernessViewModel =
        context.watch<InsertionHeatedSensoryTendernessViewModel>();

    return Scaffold(
      appBar: const CustomAppBar(title: '연도 추가 입력'),
      resizeToAvoidBottomInset: false,
      body: Stack(
        children: [
          Container(
            margin: EdgeInsets.symmetric(horizontal: 40.w),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                SizedBox(height: 24.h),

                // 연도 표시
                insertionHeatedSensoryTendernessViewModel.check
                    ? Column(
                        children: [
                          // 3일 이상인 경우 3일차 partEval 표시
                          insertionHeatedSensoryTendernessViewModel.checkDate[0]
                              ? Column(
                                  children: [
                                    const DataTitle(
                                      korText: '연도',
                                      engText: '3일차 Tenderness',
                                    ),
                                    SizedBox(height: 16.h),
                                    PartEval(
                                      selectedText: text,
                                      value:
                                          insertionHeatedSensoryTendernessViewModel
                                              .tenderness3,
                                      onChanged: (value) =>
                                          insertionHeatedSensoryTendernessViewModel
                                              .onChangedTenderness3(value),
                                    ),
                                    SizedBox(height: 32.h),
                                  ],
                                )
                              : Container(),

                          // 7일 이상인 경우 7일차 partEval 표시
                          insertionHeatedSensoryTendernessViewModel.checkDate[1]
                              ? Column(
                                  children: [
                                    const DataTitle(
                                      korText: '연도',
                                      engText: '7일차 Tenderness',
                                    ),
                                    SizedBox(height: 16.h),
                                    PartEval(
                                      selectedText: text,
                                      value:
                                          insertionHeatedSensoryTendernessViewModel
                                              .tenderness7,
                                      onChanged: (value) =>
                                          insertionHeatedSensoryTendernessViewModel
                                              .onChangedTenderness7(value),
                                    ),
                                    SizedBox(height: 32.h),
                                  ],
                                )
                              : Container(),

                          // 14일 이상인 경우 14일차 partEval 표시
                          insertionHeatedSensoryTendernessViewModel.checkDate[2]
                              ? Column(
                                  children: [
                                    const DataTitle(
                                      korText: '연도',
                                      engText: '14일차 Tenderness',
                                    ),
                                    SizedBox(height: 16.h),
                                    PartEval(
                                      selectedText: text,
                                      value:
                                          insertionHeatedSensoryTendernessViewModel
                                              .tenderness14,
                                      onChanged: (value) =>
                                          insertionHeatedSensoryTendernessViewModel
                                              .onChangedTenderness14(value),
                                    ),
                                    SizedBox(height: 32.h),
                                  ],
                                )
                              : Container(),

                          // 21일 이상인 경우 21일차 partEval 표시
                          insertionHeatedSensoryTendernessViewModel.checkDate[2]
                              ? Column(
                                  children: [
                                    const DataTitle(
                                      korText: '연도',
                                      engText: '21일차 Tenderness',
                                    ),
                                    SizedBox(height: 16.h),
                                    PartEval(
                                      selectedText: text,
                                      value:
                                          insertionHeatedSensoryTendernessViewModel
                                              .tenderness21,
                                      onChanged: (value) =>
                                          insertionHeatedSensoryTendernessViewModel
                                              .onChangedTenderness21(value),
                                    ),
                                    SizedBox(height: 32.h),
                                  ],
                                )
                              : Container(),
                        ],
                      )
                    : Expanded(
                        child: Center(
                          child: Text(
                            '연도 추가 등록 가능한 날이 아닙니다!',
                            style: Palette.h4Regular,
                          ),
                        ),
                      ),
              ],
            ),
          )
        ],
      ),
    );
  }
}

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
import 'package:structure/viewModel/data_management/researcher/insertion_heated_sensory_add_view_model.dart';

class InsertionHeatedSensoryAddScreen extends StatefulWidget {
  const InsertionHeatedSensoryAddScreen({super.key});

  @override
  State<InsertionHeatedSensoryAddScreen> createState() =>
      _InsertionHeatedSensoryAddScreenState();
}

class _InsertionHeatedSensoryAddScreenState
    extends State<InsertionHeatedSensoryAddScreen> {
  List<String> text = ['Tenderness', '연도', '질김', '', '보통', '', '연함'];
  List<String> period = ['3일차', '7일차', '14일차', '21일차'];

  @override
  Widget build(BuildContext context) {
    InsertionHeatedSensoryAddViewModel insertionHeatedSensoryAddViewModel =
        context.watch<InsertionHeatedSensoryAddViewModel>();
    return Scaffold(
      appBar: const CustomAppBar(
        title: 'Tenderness 연도 추가 입력',
        backButton: true,
      ),
      body: Stack(
        children: [
          Container(
            margin: EdgeInsets.symmetric(horizontal: 40.w),
            child: Column(
              children: [
                SizedBox(height: 24.h),
                Container(
                  alignment: Alignment.topLeft,
                  child: insertionHeatedSensoryAddViewModel.check
                      ? Column(
                          children: [
                            //3일 이상인 경우 3일차 partEval 표시
                            insertionHeatedSensoryAddViewModel.checkDate[0]
                                ? Column(
                                    children: [
                                      const DataTitle(
                                          korText: '연도',
                                          engText: '3일차 Tenderness'),
                                      SizedBox(height: 16.h),
                                      PartEval(
                                        selectedText: text,
                                        value:
                                            insertionHeatedSensoryAddViewModel
                                                .tenderness,
                                        onChanged: null,
                                      ),
                                      SizedBox(height: 16.h),
                                    ],
                                  )
                                : Container(),
                            //7일 이상인 경우 7일차 partEval 표시
                            insertionHeatedSensoryAddViewModel.checkDate[1]
                                ? Column(
                                    children: [
                                      SizedBox(height: 16.h),
                                      const DataTitle(
                                          korText: '연도',
                                          engText: '7일차 Tenderness'),
                                      SizedBox(height: 16.h),
                                      PartEval(
                                        selectedText: text,
                                        value:
                                            insertionHeatedSensoryAddViewModel
                                                .tenderness,
                                        onChanged: null,
                                      ),
                                      SizedBox(height: 16.h),
                                    ],
                                  )
                                : Container(),
                            //14일 이상인 경우 14일차 partEval 표시
                            insertionHeatedSensoryAddViewModel.checkDate[2]
                                ? Column(
                                    children: [
                                      SizedBox(height: 16.h),
                                      const DataTitle(
                                          korText: '연도',
                                          engText: '14일차 Tenderness'),
                                      SizedBox(height: 16.h),
                                      PartEval(
                                        selectedText: text,
                                        value:
                                            insertionHeatedSensoryAddViewModel
                                                .tenderness,
                                        onChanged: null,
                                      ),
                                      SizedBox(height: 16.h),
                                    ],
                                  )
                                : Container(),
                            //21일 이상인 경우 21일차 partEval 표시
                            insertionHeatedSensoryAddViewModel.checkDate[2]
                                ? Column(
                                    children: [
                                      SizedBox(height: 16.h),
                                      const DataTitle(
                                          korText: '연도',
                                          engText: '21일차 Tenderness'),
                                      SizedBox(height: 16.h),
                                      PartEval(
                                        selectedText: text,
                                        value:
                                            insertionHeatedSensoryAddViewModel
                                                .tenderness,
                                        onChanged: null,
                                      ),
                                      SizedBox(height: 16.h),
                                    ],
                                  )
                                : Container(),
                          ],
                        )
                      : const Text("tenderness 등록 가능한 날이 아닙니다!"),
                ),
                SizedBox(height: 32.h),
              ],
            ),
          )
        ],
      ),
    );
  }
}

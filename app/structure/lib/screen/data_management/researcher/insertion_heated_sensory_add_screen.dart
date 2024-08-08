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
        title: '연도 추가 입력',
        backButton: true,
        closeButton: false,
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
                  child: Text(
                      "${insertionHeatedSensoryAddViewModel.seqNo}회차 딥에이징"),
                ),
                // Container(
                //   alignment: Alignment.topLeft,
                //   child: Text(
                //       "${insertionHeatedSensoryAddViewModel}회차 딥에이징"),
                // ),
                IconButton(
                    onPressed: insertionHeatedSensoryAddViewModel.calculateDiff,
                    icon: const Icon(Icons.abc)),
                Container(
                  alignment: Alignment.topLeft,
                  child: Text(period[1]),
                ),
                const DataTitle(korText: '연도', engText: 'Tenderness'),
                SizedBox(height: 16.h),
                PartEval(
                  selectedText: text,
                  value: insertionHeatedSensoryAddViewModel.tenderness,
                  onChanged: null,
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

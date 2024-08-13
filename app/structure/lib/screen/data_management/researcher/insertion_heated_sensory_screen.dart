//
//
// 가열육 관능평가 페이지(View)
//
//

import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/data_title.dart';
import 'package:structure/components/loading_screen.dart';
import 'package:structure/components/main_button.dart';
import 'package:structure/components/part_eval.dart';
import 'package:structure/config/palette.dart';
import 'package:structure/viewModel/data_management/researcher/insertion_heated_sensory_view_model.dart';

class InsertionHeatedSensoryScreen extends StatefulWidget {
  const InsertionHeatedSensoryScreen({super.key});

  @override
  State<InsertionHeatedSensoryScreen> createState() => _HeatedMeatEvaluation();
}

class _HeatedMeatEvaluation extends State<InsertionHeatedSensoryScreen>
    with SingleTickerProviderStateMixin {
  // 가열육 관능평가 label
  List<List<String>> text = [
    ['Flavor', '풍미', '약간', '', '약간 풍부함', '', '풍부함'],
    ['Juiciness', '다즙성', '퍽퍽함', '', '보통', '', '다즙합'],
    ['Tenderness', '연도', '질김', '', '보통', '', '연함'],
    ['Umami', '표면육즙', '약함', '', '보통', '', '좋음'],
    ['Palatability', '기호도', '나쁨', '', '보통', '', '좋음'],
  ];

  @override
  Widget build(BuildContext context) {
    InsertionHeatedSensoryViewModel insertionHeatedSensoryViewModel =
        context.watch<InsertionHeatedSensoryViewModel>();

    return Scaffold(
      appBar: CustomAppBar(
        title: '가열육 관능평가',
        actionButton: insertionHeatedSensoryViewModel.meatModel.seqno != 0
            ? IconButton(
                onPressed: () {
                  insertionHeatedSensoryViewModel.clickedTendernessAdd(context);
                },
                icon: const Icon(Icons.timer),
                color: Colors.black,
              )
            : null,
      ),
      body: Stack(
        children: [
          Container(
            margin: EdgeInsets.symmetric(horizontal: 40.w),
            child: Column(
              children: [
                SizedBox(height: 24.h),

                // 'PartEval' 컴포넌트를 이용하여 관능평가 항목을 정의.
                const DataTitle(korText: '풍미', engText: 'Flavor'),
                SizedBox(height: 16.h),

                PartEval(
                  selectedText: text[0],
                  value: insertionHeatedSensoryViewModel.flavor,
                  onChanged: (value) =>
                      insertionHeatedSensoryViewModel.onChangedFlavor(value),
                ),
                SizedBox(height: 32.h),

                const DataTitle(korText: '다즙성', engText: 'Juiciness'),
                SizedBox(height: 16.h),

                PartEval(
                  selectedText: text[1],
                  value: insertionHeatedSensoryViewModel.juiciness,
                  onChanged: (value) =>
                      insertionHeatedSensoryViewModel.onChangedJuiciness(value),
                ),
                SizedBox(height: 32.h),

                const DataTitle(korText: '연도', engText: 'Tenderness'),
                SizedBox(height: 16.h),

                PartEval(
                  selectedText: text[2],
                  value: insertionHeatedSensoryViewModel.tenderness0,
                  onChanged: (value) => insertionHeatedSensoryViewModel
                      .onChangedTenderness(value),
                ),
                SizedBox(height: 32.h),

                const DataTitle(korText: '감칠맛', engText: 'Umami'),
                SizedBox(height: 16.h),

                PartEval(
                  selectedText: text[3],
                  value: insertionHeatedSensoryViewModel.umami,
                  onChanged: (value) =>
                      insertionHeatedSensoryViewModel.onChangedUmami(value),
                ),
                SizedBox(height: 32.h),

                const DataTitle(korText: '기호도', engText: 'Palatability'),
                SizedBox(height: 16.h),

                PartEval(
                  selectedText: text[4],
                  value: insertionHeatedSensoryViewModel.palatability,
                  onChanged: (value) => insertionHeatedSensoryViewModel
                      .onChangedPalatability(value),
                ),
                const Spacer(),

                // 데이터 저장 버튼
                Container(
                  margin: EdgeInsets.only(bottom: 40.h),
                  child: MainButton(
                    width: double.infinity,
                    height: 96.h,
                    text: '저장',
                    onPressed: () =>
                        insertionHeatedSensoryViewModel.saveData(context),
                  ),
                ),
              ],
            ),
          ),
          insertionHeatedSensoryViewModel.isLoading
              ? const Center(child: LoadingScreen())
              : Container()
        ],
      ),
    );
  }
}

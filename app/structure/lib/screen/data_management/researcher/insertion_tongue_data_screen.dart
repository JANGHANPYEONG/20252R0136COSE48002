//
//
// 전자혀 데이터 페이지(View)
//
//

import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/data_field.dart';
import 'package:structure/components/loading_screen.dart';
import 'package:structure/components/main_button.dart';
import 'package:structure/viewModel/data_management/researcher/insertion_tongue_data_view_model.dart';

class InsertionTongueDataScreen extends StatefulWidget {
  const InsertionTongueDataScreen({super.key});

  @override
  State<InsertionTongueDataScreen> createState() =>
      _InsertionTongueDataScreenState();
}

class _InsertionTongueDataScreenState extends State<InsertionTongueDataScreen> {
  @override
  Widget build(BuildContext context) {
    InsertionTongueDataViewModel insertionTongueDataViewModel =
        context.watch<InsertionTongueDataViewModel>();

    return GestureDetector(
      // 키보드 unfocus
      onTap: () => FocusScope.of(context).unfocus(),
      child: Scaffold(
        appBar: CustomAppBar(
          title: insertionTongueDataViewModel.title,
          backButton: true,
          closeButton: false,
        ),
        resizeToAvoidBottomInset: false,
        body: Stack(
          children: [
            Container(
              margin: EdgeInsets.symmetric(horizontal: 40.w),
              child: Column(
                children: [
                  SizedBox(height: 24.h),

                  // 신맛
                  DataField(
                    mainText: 'Sourness',
                    subText: '신맛',
                    controller: insertionTongueDataViewModel.sourness,
                    onChangeFunc: (_) =>
                        insertionTongueDataViewModel.inputCheck(),
                  ),
                  SizedBox(height: 32.h),

                  // 진한맛
                  DataField(
                      mainText: 'Bitterness',
                      subText: '진한맛',
                      controller: insertionTongueDataViewModel.bitterness,
                      onChangeFunc: (_) =>
                          insertionTongueDataViewModel.inputCheck()),
                  SizedBox(height: 32.h),

                  // 감칠맛
                  DataField(
                      mainText: 'Umami',
                      subText: '감칠맛',
                      controller: insertionTongueDataViewModel.umami,
                      onChangeFunc: (_) =>
                          insertionTongueDataViewModel.inputCheck()),
                  SizedBox(height: 32.h),

                  // 후미
                  DataField(
                      isFinal: 1,
                      mainText: 'Richness',
                      subText: '후미',
                      controller: insertionTongueDataViewModel.richness,
                      onChangeFunc: (_) =>
                          insertionTongueDataViewModel.inputCheck()),
                  const Spacer(),

                  // 데이터 저장 버튼
                  Container(
                    margin: EdgeInsets.only(bottom: 40.h),
                    child: MainButton(
                      width: double.infinity,
                      height: 96.h,
                      text: '저장',
                      onPressed: insertionTongueDataViewModel.inputComplete
                          ? () async =>
                              insertionTongueDataViewModel.saveData(context)
                          : null,
                    ),
                  ),
                ],
              ),
            ),
            insertionTongueDataViewModel.isLoading
                ? const LoadingScreen()
                : Container()
          ],
        ),
      ),
    );
  }
}

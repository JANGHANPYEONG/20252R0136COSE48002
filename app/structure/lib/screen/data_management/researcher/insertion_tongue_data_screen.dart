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
    return GestureDetector(
      onTap: () {
        // 키보드 unfocus
        FocusScope.of(context).unfocus();
      },
      child: Scaffold(
        backgroundColor: Colors.white,
        appBar: const CustomAppBar(
          title: '전자혀 데이터',
          backButton: true,
          closeButton: false,
        ),
        body: SingleChildScrollView(
          child: Stack(
            children: [
              Column(
                // 'datafield' 컴포넌트를 이용하여 전자혀 데이터 측정
                children: [
                  SizedBox(
                    height: 30.h,
                  ),
                  DataField(
                    mainText: 'Sourness',
                    subText: '신맛',
                    controller:
                        context.read<InsertionTongueDataViewModel>().sourness,
                  ),
                  SizedBox(
                    height: 112.h,
                  ),
                  DataField(
                    mainText: 'Bitterness',
                    subText: '진한맛',
                    controller:
                        context.read<InsertionTongueDataViewModel>().bitterness,
                  ),
                  SizedBox(
                    height: 112.h,
                  ),
                  DataField(
                    mainText: 'Umami',
                    subText: '감칠맛',
                    controller:
                        context.read<InsertionTongueDataViewModel>().umami,
                  ),
                  SizedBox(
                    height: 112.h,
                  ),
                  DataField(
                    mainText: 'Richness',
                    subText: '후미',
                    controller:
                        context.read<InsertionTongueDataViewModel>().richness,
                  ),
                  // SizedBox(
                  //   height: 200.h,
                  // ),
                  // 데이터 저장 버튼
                  Container(
                    margin: EdgeInsets.only(bottom: 28.h, top: 150.h),
                    child: MainButton(
                      onPressed: () async => context
                          .read<InsertionTongueDataViewModel>()
                          .saveData(context),
                      text: '저장',
                      width: 658.w,
                      height: 96.h,
                      mode: 1,
                    ),
                  ),
                ],
              ),
              context.watch<InsertionTongueDataViewModel>().isLoading
                  ? const LoadingScreen()
                  : Container()
            ],
          ),
        ),
      ),
    );
  }
}

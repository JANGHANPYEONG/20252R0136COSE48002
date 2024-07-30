//
//
// 실험 데이터 페이지(View)
//
//

import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/data_field.dart';
import 'package:structure/components/loading_screen.dart';
import 'package:structure/components/main_button.dart';
import 'package:structure/viewModel/data_management/researcher/insertion_lab_data_view_model.dart';

class InsertionLabDataScreen extends StatefulWidget {
  const InsertionLabDataScreen({super.key});

  @override
  State<InsertionLabDataScreen> createState() => _InsertionLabDataScreenState();
}

class _InsertionLabDataScreenState extends State<InsertionLabDataScreen> {
  @override
  Widget build(BuildContext context) {
    InsertionLabDataViewModel insertionLabDataViewModel =
        context.watch<InsertionLabDataViewModel>();

    return GestureDetector(
      onTap: () {
        // 키보드 unfocus
        FocusScope.of(context).unfocus();
      },
      child: Scaffold(
        backgroundColor: Colors.white,
        appBar: CustomAppBar(
          title: insertionLabDataViewModel.title,
          backButton: true,
          closeButton: false,
        ),
        body: Stack(
          children: [
            SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  DataField(
                    mainText: 'L ',
                    subText: '명도',
                    controller: insertionLabDataViewModel.l,
                    onChangeFunc: (_) => insertionLabDataViewModel.inputCheck(),
                  ),
                  SizedBox(height: 32.h),

                  DataField(
                    mainText: 'a ',
                    subText: '적색도',
                    unit: '',
                    controller: insertionLabDataViewModel.a,
                    onChangeFunc: (_) => insertionLabDataViewModel.inputCheck(),
                  ),
                  SizedBox(height: 32.h),

                  DataField(
                    mainText: 'b ',
                    subText: '황색도',
                    unit: '',
                    controller: insertionLabDataViewModel.b,
                    onChangeFunc: (_) => insertionLabDataViewModel.inputCheck(),
                  ),
                  SizedBox(height: 32.h),

                  DataField(
                    mainText: 'DL ',
                    subText: '육즙감량',
                    unit: '%',
                    controller: insertionLabDataViewModel.dl,
                    isPercent: true,
                    onChangeFunc: (_) => insertionLabDataViewModel.inputCheck(),
                  ),
                  SizedBox(height: 32.h),

                  DataField(
                    mainText: 'CL ',
                    subText: '가열감량',
                    unit: '%',
                    controller: insertionLabDataViewModel.cl,
                    isPercent: true,
                    onChangeFunc: (_) => insertionLabDataViewModel.inputCheck(),
                  ),
                  SizedBox(height: 32.h),

                  DataField(
                    mainText: 'RW ',
                    subText: '압착감량',
                    unit: '%',
                    controller: insertionLabDataViewModel.rw,
                    isPercent: true,
                    onChangeFunc: (_) => insertionLabDataViewModel.inputCheck(),
                  ),
                  SizedBox(height: 32.h),

                  DataField(
                    mainText: 'pH ',
                    subText: '산도',
                    controller: insertionLabDataViewModel.ph,
                    onChangeFunc: (_) => insertionLabDataViewModel.inputCheck(),
                  ),
                  SizedBox(height: 32.h),

                  DataField(
                    mainText: 'WBSF ',
                    subText: '전단가',
                    unit: 'kgf',
                    controller: insertionLabDataViewModel.wbsf,
                    onChangeFunc: (_) => insertionLabDataViewModel.inputCheck(),
                  ),
                  SizedBox(height: 32.h),

                  DataField(
                    mainText: '카텝신활성도',
                    subText: '',
                    controller: insertionLabDataViewModel.ct,
                    onChangeFunc: (_) => insertionLabDataViewModel.inputCheck(),
                  ),
                  SizedBox(height: 32.h),

                  DataField(
                    mainText: 'MFI ',
                    subText: '근소편화지수',
                    controller: insertionLabDataViewModel.mfi,
                    onChangeFunc: (_) => insertionLabDataViewModel.inputCheck(),
                  ),
                  DataField(
                      isFinal: 1,
                      mainText: 'Collagen ',
                      subText: '콜라겐',
                      controller:
                          context.read<InsertionLabDataViewModel>().collagen),
                  SizedBox(height: 32.h),

                  DataField(
                    mainText: 'Collagen ',
                    subText: '콜라겐',
                    controller: insertionLabDataViewModel.collagen,
                    onChangeFunc: (_) => insertionLabDataViewModel.inputCheck(),
                  ),
                  SizedBox(height: 64.h),

                  // 저장 버튼
                  Container(
                    margin: EdgeInsets.fromLTRB(40.w, 0, 40.w, 40.w),
                    child: MainButton(
                      onPressed: insertionLabDataViewModel.inputComplete
                          ? () async =>
                              insertionLabDataViewModel.saveData(context)
                          : null,
                      text: '저장',
                      width: double.infinity,
                      height: 96.h,
                      mode: 1,
                    ),
                  ),
                ],
              ),
            ),
            insertionLabDataViewModel.isLoading
                ? const Center(child: LoadingScreen())
                : Container()
          ],
        ),
      ),
    );
  }
}

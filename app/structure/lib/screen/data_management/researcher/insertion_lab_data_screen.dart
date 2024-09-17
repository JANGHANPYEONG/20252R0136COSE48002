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
      onTap: () => FocusScope.of(context).unfocus(),
      child: Scaffold(
        appBar: CustomAppBar(title: insertionLabDataViewModel.title),
        body: Stack(
          children: [
            SingleChildScrollView(
              child: Container(
                margin: EdgeInsets.symmetric(horizontal: 40.w),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    SizedBox(height: 24.h),

                    Form(
                      key: insertionLabDataViewModel.formKey,
                      child: Column(
                        children: [
                          DataField(
                            mainText: 'L ',
                            subText: '명도',
                            controller: insertionLabDataViewModel.l,
                            onChangeFunc: (_) =>
                                insertionLabDataViewModel.inputCheck(),
                            validateFunc: (value) => insertionLabDataViewModel
                                .validate(value, 1, 30),
                            formKey: insertionLabDataViewModel.formKey,
                            onEditingComplete: () {
                              insertionLabDataViewModel.formKey.currentState
                                  ?.validate();
                              FocusScope.of(context).nextFocus();
                            },
                          ),
                          SizedBox(height: 32.h),
                          DataField(
                            mainText: 'a ',
                            subText: '적색도',
                            validateFunc: (value) => insertionLabDataViewModel
                                .validate(value, 1, 30),
                            controller: insertionLabDataViewModel.a,
                            onChangeFunc: (_) =>
                                insertionLabDataViewModel.inputCheck(),
                            formKey: insertionLabDataViewModel.formKey,
                            onEditingComplete: () {
                              insertionLabDataViewModel.formKey.currentState
                                  ?.validate();
                              FocusScope.of(context).nextFocus();
                            },
                          ),
                          SizedBox(height: 32.h),
                          DataField(
                            mainText: 'b ',
                            subText: '황색도',
                            controller: insertionLabDataViewModel.b,
                            onChangeFunc: (_) =>
                                insertionLabDataViewModel.inputCheck(),
                            validateFunc: (value) => insertionLabDataViewModel
                                .validate(value, 1, 30),
                            formKey: insertionLabDataViewModel.formKey,
                            onEditingComplete: () {
                              insertionLabDataViewModel.formKey.currentState
                                  ?.validate();
                              FocusScope.of(context).nextFocus();
                            },
                          ),
                          SizedBox(height: 32.h),
                          DataField(
                            mainText: 'DL ',
                            subText: '육즙감량',
                            unit: '%',
                            controller: insertionLabDataViewModel.dl,
                            onChangeFunc: (_) =>
                                insertionLabDataViewModel.inputCheck(),
                            validateFunc: (value) => insertionLabDataViewModel
                                .validate(value, 0, 100),
                            formKey: insertionLabDataViewModel.formKey,
                            onEditingComplete: () {
                              insertionLabDataViewModel.formKey.currentState
                                  ?.validate();
                              FocusScope.of(context).nextFocus();
                            },
                          ),
                          SizedBox(height: 32.h),
                          DataField(
                            mainText: 'CL ',
                            subText: '가열감량',
                            unit: '%',
                            controller: insertionLabDataViewModel.cl,
                            onChangeFunc: (_) =>
                                insertionLabDataViewModel.inputCheck(),
                            validateFunc: (value) => insertionLabDataViewModel
                                .validate(value, 0, 100),
                            formKey: insertionLabDataViewModel.formKey,
                            onEditingComplete: () {
                              insertionLabDataViewModel.formKey.currentState
                                  ?.validate();
                              FocusScope.of(context).nextFocus();
                            },
                          ),
                          SizedBox(height: 32.h),
                          DataField(
                            mainText: 'RW ',
                            subText: '압착감량',
                            unit: '%',
                            controller: insertionLabDataViewModel.rw,
                            onChangeFunc: (_) =>
                                insertionLabDataViewModel.inputCheck(),
                            validateFunc: (value) => insertionLabDataViewModel
                                .validate(value, 0, 100),
                            formKey: insertionLabDataViewModel.formKey,
                            onEditingComplete: () {
                              insertionLabDataViewModel.formKey.currentState
                                  ?.validate();
                              FocusScope.of(context).nextFocus();
                            },
                          ),
                          SizedBox(height: 32.h),
                          DataField(
                            mainText: 'pH ',
                            subText: '산도',
                            controller: insertionLabDataViewModel.ph,
                            onChangeFunc: (_) =>
                                insertionLabDataViewModel.inputCheck(),
                            validateFunc: (value) => insertionLabDataViewModel
                                .validate(value, 0, 14),
                            formKey: insertionLabDataViewModel.formKey,
                            onEditingComplete: () {
                              insertionLabDataViewModel.formKey.currentState
                                  ?.validate();
                              FocusScope.of(context).nextFocus();
                            },
                          ),
                          SizedBox(height: 32.h),
                          DataField(
                            mainText: 'WBSF ',
                            subText: '전단가',
                            unit: 'kgf',
                            controller: insertionLabDataViewModel.wbsf,
                            onChangeFunc: (_) =>
                                insertionLabDataViewModel.inputCheck(),
                            validateFunc: (value) =>
                                insertionLabDataViewModel.validate(value, 1, 6),
                            formKey: insertionLabDataViewModel.formKey,
                            onEditingComplete: () {
                              insertionLabDataViewModel.formKey.currentState
                                  ?.validate();
                              FocusScope.of(context).nextFocus();
                            },
                          ),
                          SizedBox(height: 32.h),
                          DataField(
                            mainText: 'Cathepsin',
                            subText: '카텝신활성도',
                            controller: insertionLabDataViewModel.ct,
                            onChangeFunc: (_) =>
                                insertionLabDataViewModel.inputCheck(),
                            validateFunc: (value) => insertionLabDataViewModel
                                .validate(value, 1, 10000),
                            formKey: insertionLabDataViewModel.formKey,
                            onEditingComplete: () {
                              insertionLabDataViewModel.formKey.currentState
                                  ?.validate();
                              FocusScope.of(context).nextFocus();
                            },
                          ),
                          SizedBox(height: 32.h),
                          DataField(
                            mainText: 'MFI ',
                            subText: '근소편화지수',
                            controller: insertionLabDataViewModel.mfi,
                            onChangeFunc: (_) =>
                                insertionLabDataViewModel.inputCheck(),
                            validateFunc: (value) => insertionLabDataViewModel
                                .validate(value, 1, 250),
                            formKey: insertionLabDataViewModel.formKey,
                            onEditingComplete: () {
                              insertionLabDataViewModel.formKey.currentState
                                  ?.validate();
                              FocusScope.of(context).nextFocus();
                            },
                          ),
                          SizedBox(height: 32.h),
                          DataField(
                            mainText: 'Collagen ',
                            subText: '콜라겐',
                            controller: insertionLabDataViewModel.collagen,
                            isFinal: true,
                            onChangeFunc: (_) =>
                                insertionLabDataViewModel.inputCheck(),
                            validateFunc: (value) => insertionLabDataViewModel
                                .validate(value, 0, 10),
                            formKey: insertionLabDataViewModel.formKey,
                            onEditingComplete: () {
                              insertionLabDataViewModel.formKey.currentState
                                  ?.validate();
                              FocusScope.of(context).unfocus();
                            },
                          ),
                          SizedBox(height: 32.h),
                        ],
                      ),
                    ),
                    SizedBox(height: 64.h),

                    // 저장 버튼
                    Container(
                      margin: EdgeInsets.only(bottom: 40.h),
                      child: MainButton(
                        width: double.infinity,
                        height: 96.h,
                        text: '저장',
                        onPressed: insertionLabDataViewModel.inputComplete
                            ? () async => insertionLabDataViewModel.saveData()
                            : null,
                      ),
                    ),
                  ],
                ),
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

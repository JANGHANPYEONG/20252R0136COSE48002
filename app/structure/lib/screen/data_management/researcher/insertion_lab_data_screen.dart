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
  final GlobalKey<FormState> _formKey = GlobalKey<FormState>();

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
                      key: _formKey,
                      child: Column(
                        children: [
                          DataField(
                            mainText: 'L ',
                            subText: '명도',
                            // isL: true,
                            validateFunc: (value) {
                              double parsedValue =
                                  double.tryParse(value!) ?? 0.0;
                              if (parsedValue < 1 || parsedValue > 30) {
                                return "1~30 사이의 값을 입력하세요.";
                              }
                              return null;
                            },
                            // type: 'L',
                            controller: insertionLabDataViewModel.l,
                            onChangeFunc: (_) =>
                                insertionLabDataViewModel.inputCheck(),
                            formKey: _formKey,
                            onEditingComplete: () {
                              _formKey.currentState?.validate();
                            },
                          ),
                          SizedBox(height: 32.h),
                          DataField(
                            mainText: 'a ',
                            subText: '적색도',
                            // type: 'a',
                            unit: '',
                            validateFunc: (value) {
                              double parsedValue =
                                  double.tryParse(value!) ?? 0.0;
                              if (parsedValue < 1 || parsedValue > 30) {
                                return "1~30 사이의 값을 입력하세요.";
                              }
                              return null;
                            },
                            controller: insertionLabDataViewModel.a,
                            onChangeFunc: (_) =>
                                insertionLabDataViewModel.inputCheck(),
                            formKey: _formKey,
                            onEditingComplete: () {
                              _formKey.currentState?.validate();
                            },
                          ),
                          SizedBox(height: 32.h),
                          DataField(
                            mainText: 'b ',
                            subText: '황색도',
                            // type: 'b',
                            unit: '',
                            controller: insertionLabDataViewModel.b,
                            onChangeFunc: (_) =>
                                insertionLabDataViewModel.inputCheck(),
                            validateFunc: (value) {
                              double parsedValue =
                                  double.tryParse(value!) ?? 0.0;
                              if (parsedValue < 1 || parsedValue > 30) {
                                return "1~30 사이의 값을 입력하세요.";
                              }
                              return null;
                            },
                            formKey: _formKey,
                            onEditingComplete: () {
                              _formKey.currentState?.validate();
                            },
                          ),
                          SizedBox(height: 32.h),
                          DataField(
                            mainText: 'DL ',
                            subText: '육즙감량',
                            // isPercent: true,
                            unit: '%',
                            controller: insertionLabDataViewModel.dl,
                            onChangeFunc: (_) =>
                                insertionLabDataViewModel.inputCheck(),
                            validateFunc: (value) {
                              double parsedValue =
                                  double.tryParse(value!) ?? 0.0;
                              if (parsedValue < 0 || parsedValue > 100) {
                                return "0~100 사이의 값을 입력하세요.";
                              }
                              return null;
                            },
                            formKey: _formKey,
                            onEditingComplete: () {
                              _formKey.currentState?.validate();
                            },
                          ),
                          SizedBox(height: 32.h),
                          DataField(
                            mainText: 'CL ',
                            subText: '가열감량',
                            // isPercent: true,
                            unit: '%',
                            controller: insertionLabDataViewModel.cl,
                            onChangeFunc: (_) =>
                                insertionLabDataViewModel.inputCheck(),
                            validateFunc: (value) {
                              double parsedValue =
                                  double.tryParse(value!) ?? 0.0;
                              if (parsedValue < 0 || parsedValue > 100) {
                                return "0~100 사이의 값을 입력하세요.";
                              }
                              return null;
                            },
                            formKey: _formKey,
                            onEditingComplete: () {
                              _formKey.currentState?.validate();
                            },
                          ),
                          SizedBox(height: 32.h),
                          DataField(
                            mainText: 'RW ',
                            subText: '압착감량',
                            // isPercent: true,
                            unit: '%',
                            controller: insertionLabDataViewModel.rw,
                            onChangeFunc: (_) =>
                                insertionLabDataViewModel.inputCheck(),
                            validateFunc: (value) {
                              double parsedValue =
                                  double.tryParse(value!) ?? 0.0;
                              if (parsedValue < 0 || parsedValue > 100) {
                                return "0~100 사이의 값을 입력하세요.";
                              }
                              return null;
                            },
                            formKey: _formKey,
                            onEditingComplete: () {
                              _formKey.currentState?.validate();
                            },
                          ),
                          SizedBox(height: 32.h),
                          DataField(
                            mainText: 'pH ',
                            subText: '산도',
                            // type: 'ph',
                            controller: insertionLabDataViewModel.ph,
                            onChangeFunc: (_) =>
                                insertionLabDataViewModel.inputCheck(),
                            validateFunc: (value) {
                              double parsedValue =
                                  double.tryParse(value!) ?? 0.0;
                              if (parsedValue < 0 || parsedValue > 14) {
                                return "0~14 사이의 값을 입력하세요.";
                              }
                              return null;
                            },
                            formKey: _formKey,
                            onEditingComplete: () {
                              _formKey.currentState?.validate();
                            },
                          ),
                          SizedBox(height: 32.h),
                          DataField(
                            mainText: 'WBSF ',
                            subText: '전단가',
                            // type: 'WSBF',
                            unit: 'kgf',
                            controller: insertionLabDataViewModel.wbsf,
                            onChangeFunc: (_) =>
                                insertionLabDataViewModel.inputCheck(),
                            validateFunc: (value) {
                              double parsedValue =
                                  double.tryParse(value!) ?? 0.0;
                              if (parsedValue < 1 || parsedValue > 6) {
                                return "0~6 사이의 값을 입력하세요.";
                              }
                              return null;
                            },
                            formKey: _formKey,
                            onEditingComplete: () {
                              _formKey.currentState?.validate();
                            },
                          ),
                          SizedBox(height: 32.h),
                          DataField(
                            mainText: 'Cathepsin',
                            subText: '카텝신활성도',
                            // type: 'Cathepsin',
                            controller: insertionLabDataViewModel.ct,
                            onChangeFunc: (_) =>
                                insertionLabDataViewModel.inputCheck(),
                            validateFunc: (value) {
                              double parsedValue =
                                  double.tryParse(value!) ?? 0.0;
                              if (parsedValue < 0 || parsedValue > 10000) {
                                return "0~10000 사이의 값을 입력하세요.";
                              }
                              return null;
                            },
                            formKey: _formKey,
                            onEditingComplete: () {
                              _formKey.currentState?.validate();
                            },
                          ),
                          SizedBox(height: 32.h),
                          DataField(
                            mainText: 'MFI ',
                            subText: '근소편화지수',
                            // type: 'MFI',
                            controller: insertionLabDataViewModel.mfi,
                            onChangeFunc: (_) =>
                                insertionLabDataViewModel.inputCheck(),
                            validateFunc: (value) {
                              double parsedValue =
                                  double.tryParse(value!) ?? 0.0;
                              if (parsedValue < 1 || parsedValue > 250) {
                                return "1~250 사이의 값을 입력하세요.";
                              }
                              return null;
                            },
                            formKey: _formKey,
                            onEditingComplete: () {
                              _formKey.currentState?.validate();
                            },
                          ),
                          SizedBox(height: 32.h),
                          DataField(
                            mainText: 'Collagen ',
                            subText: '콜라겐',
                            // type: 'Collagen',
                            controller: insertionLabDataViewModel.collagen,
                            isFinal: true,
                            onChangeFunc: (_) =>
                                insertionLabDataViewModel.inputCheck(),
                            validateFunc: (value) {
                              double parsedValue =
                                  double.tryParse(value!) ?? 0.0;
                              if (parsedValue < 0 || parsedValue > 10) {
                                return "0~10 사이의 값을 입력하세요.";
                              }
                              return null;
                            },
                            formKey: _formKey,
                            onEditingComplete: () {
                              _formKey.currentState?.validate();
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
                            ? () async =>
                                insertionLabDataViewModel.saveData(context)
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

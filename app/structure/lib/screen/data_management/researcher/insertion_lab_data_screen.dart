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
    return GestureDetector(
      onTap: () {
        // 키보드 unfocus
        FocusScope.of(context).unfocus();
      },
      child: Scaffold(
        backgroundColor: Colors.white,
        appBar: const CustomAppBar(
          title: '실험 데이터',
          backButton: true,
          closeButton: false,
        ),
        body: SingleChildScrollView(
          child: Stack(
            children: [
              Column(
                // 'LabDataField' 컴포넌트를 이용해서 실험 데이터 입력
                // mainAxisSize: MainAxisSize.max,
                children: [
                  SizedBox(
                    height: 20.h,
                  ),
                  DataField(
                      mainText: 'L ',
                      subText: '명도',
                      controller: context.read<InsertionLabDataViewModel>().l),
                  SizedBox(
                    height: 30.h,
                  ),
                  DataField(
                      mainText: 'a ',
                      subText: '적색도',
                      unit: '',
                      controller: context.read<InsertionLabDataViewModel>().a),
                  SizedBox(
                    height: 30.h,
                  ),
                  DataField(
                      mainText: 'b ',
                      subText: '황색도',
                      unit: '',
                      controller: context.read<InsertionLabDataViewModel>().b),
                  SizedBox(
                    height: 30.h,
                  ),
                  DataField(
                      mainText: 'DL ',
                      subText: '육즙감량',
                      unit: '%',
                      controller: context.read<InsertionLabDataViewModel>().dl,
                      isPercent: true),
                  SizedBox(
                    height: 30.h,
                  ),
                  DataField(
                      mainText: 'CL ',
                      subText: '가열감량',
                      unit: '%',
                      controller: context.read<InsertionLabDataViewModel>().cl,
                      isPercent: true),
                  SizedBox(
                    height: 30.h,
                  ),
                  DataField(
                      mainText: 'RW ',
                      subText: '압착감량',
                      unit: '%',
                      controller: context.read<InsertionLabDataViewModel>().rw,
                      isPercent: true),
                  SizedBox(
                    height: 30.h,
                  ),
                  DataField(
                      mainText: 'pH ',
                      subText: '산도',
                      controller: context.read<InsertionLabDataViewModel>().ph),
                  SizedBox(
                    height: 30.h,
                  ),
                  DataField(
                      mainText: 'WBSF ',
                      subText: '전단가',
                      unit: 'kgf',
                      controller:
                          context.read<InsertionLabDataViewModel>().wbsf),
                  SizedBox(
                    height: 30.h,
                  ),
                  DataField(
                      mainText: '카텝신활성도',
                      subText: '',
                      controller: context.read<InsertionLabDataViewModel>().ct),
                  SizedBox(
                    height: 30.h,
                  ),
                  DataField(
                      mainText: 'MFI ',
                      subText: '근소편화지수',
                      controller:
                          context.read<InsertionLabDataViewModel>().mfi),
                  SizedBox(
                    height: 30.h,
                  ),
                  DataField(
                      mainText: 'Collagen ',
                      subText: '콜라겐',
                      controller:
                          context.read<InsertionLabDataViewModel>().collagen),

                  SizedBox(
                    height: 16.h,
                  ),
                  // 저장 버튼
                  MainButton(
                    onPressed: () async => context
                        .read<InsertionLabDataViewModel>()
                        .saveData(context),
                    text: '저장',
                    width: 658.w,
                    height: 104.h,
                    mode: 1,
                  ),
                  SizedBox(
                    height: 30.h,
                  ),
                ],
              ),
              context.watch<InsertionLabDataViewModel>().isLoading
                  ? const LoadingScreen()
                  : Container()
            ],
          ),
        ),
      ),
    );
  }
}

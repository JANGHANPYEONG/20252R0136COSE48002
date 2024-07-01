//
//
// 원육 추가 페이지(View) : Researcher
//
//

import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/step_card.dart';
import 'package:structure/model/meat_model.dart';
import 'package:structure/viewModel/data_management/researcher/add_raw_meat_view_model.dart';

class StepFreshMeat extends StatelessWidget {
  final MeatModel meatModel;
  const StepFreshMeat({super.key, required this.meatModel});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: const CustomAppBar(
        title: '추가 정보 입력',
        backButton: true,
        closeButton: false,
      ),
      body: Center(
        child: Column(
          children: [
            SizedBox(
              height: 48.h,
            ),
            InkWell(
              onTap: () =>
                  context.read<AddRawMeatViewModel>().clickedHeated(context),
              child: StepCard(
                mainText: '가열육 관능평가',
                isCompleted: meatModel.heatedCompleted,
                isBefore: false,
                imageUrl: 'assets/images/meat_eval.png',
              ),
            ),
            SizedBox(
              height: 18.h,
            ),
            InkWell(
              onTap: () =>
                  context.read<AddRawMeatViewModel>().clickedTongue(context),
              child: StepCard(
                mainText: '전자혀 데이터',
                isCompleted: meatModel.tongueCompleted,
                isBefore: false,
                imageUrl: 'assets/images/meat_tongue.png',
              ),
            ),
            SizedBox(
              height: 18.h,
            ),
            InkWell(
              onTap: () =>
                  context.read<AddRawMeatViewModel>().clickedLab(context),
              child: StepCard(
                mainText: '실험 데이터',
                isCompleted: meatModel.labCompleted,
                isBefore: false,
                imageUrl: 'assets/images/meat_lab.png',
              ),
            ),
          ],
        ),
      ),
    );
  }
}

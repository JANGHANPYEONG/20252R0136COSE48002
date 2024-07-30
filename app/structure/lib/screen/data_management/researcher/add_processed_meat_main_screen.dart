//
//
// 처리육(딥에이징) 추가 페이지(View) : Researcher
//
//

import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/custom_divider.dart';
import 'package:structure/components/custom_scroll.dart';
import 'package:structure/components/step_card.dart';
import 'package:structure/model/meat_model.dart';
import 'package:structure/viewModel/data_management/researcher/add_processed_meat_view_model.dart';
import 'package:structure/components/main_button.dart';

class AddProcessedMeatMainScreen extends StatelessWidget {
  final MeatModel meatModel;
  const AddProcessedMeatMainScreen({super.key, required this.meatModel});

  @override
  Widget build(BuildContext context) {
    AddProcessedMeatViewModel addProcessedMeatViewModel =
        context.watch<AddProcessedMeatViewModel>();

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: const CustomAppBar(
        title: '추가 정보 입력',
        backButton: true,
        closeButton: false,
      ),
      body: ScrollConfiguration(
        behavior: CustomScroll(),
        child: SingleChildScrollView(
          child: Column(
            children: [
              // 처리육 단면 촬영
              StepCard(
                mainText: '처리육 단면 촬영',
                status: meatModel.imageCompleted ? 1 : 2,
                onTap: () => addProcessedMeatViewModel.clickedImage(context),
                imageUrl: 'assets/images/meat_image.png',
              ),
              SizedBox(height: 16.h),

              // 처리육 관능평가
              StepCard(
                mainText: '처리육 관능평가',
                status: meatModel.sensoryCompleted ? 1 : 2,
                onTap: () => addProcessedMeatViewModel.clickedSensory(context),
                imageUrl: 'assets/images/meat_eval.png',
              ),
              SizedBox(height: 16.h),

              // 처리육 전자혀
              StepCard(
                mainText: '처리육 전자혀 데이터',
                status: meatModel.tongueCompleted ? 1 : 2,
                onTap: () => addProcessedMeatViewModel.clickedTongue(context),
                imageUrl: 'assets/images/meat_tongue.png',
              ),
              SizedBox(height: 16.h),

              // 처리육 실험
              StepCard(
                mainText: '처리육 실험 데이터',
                status: meatModel.labCompleted ? 1 : 2,
                onTap: () => addProcessedMeatViewModel.clickedLab(context),
                imageUrl: 'assets/images/meat_lab.png',
              ),
              SizedBox(height: 16.h),

              // Divdier
              Container(
                margin: EdgeInsets.symmetric(horizontal: 40.w),
                child: const CustomDivider(),
              ),
              SizedBox(height: 16.h),

              // 가열육 단면 촬영
              StepCard(
                mainText: '가열육 단면 촬영',
                status: meatModel.heatedImageCompleted ? 1 : 2,
                onTap: () =>
                    addProcessedMeatViewModel.clickedHeatedImage(context),
                imageUrl: 'assets/images/meat_image.png',
              ),
              SizedBox(height: 16.h),

              // 가열육 관능 평가
              StepCard(
                mainText: '가열육 관능평가',
                status: meatModel.heatedSensoryCompleted ? 1 : 2,
                onTap: () =>
                    addProcessedMeatViewModel.clickedHeatedSensory(context),
                imageUrl: 'assets/images/meat_eval.png',
              ),
              SizedBox(height: 16.h),

              // 가열육 전자혀
              StepCard(
                mainText: '가열육 전자혀 데이터',
                status: meatModel.heatedTongueCompleted ? 1 : 2,
                onTap: () =>
                    addProcessedMeatViewModel.clickedHeatedTongue(context),
                imageUrl: 'assets/images/meat_tongue.png',
              ),
              SizedBox(height: 16.h),

              // 가열육 실험 데이터
              StepCard(
                mainText: '가열육 실험 데이터',
                status: meatModel.heatedLabCompleted ? 1 : 2,
                onTap: () =>
                    addProcessedMeatViewModel.clickedHeatedLab(context),
                imageUrl: 'assets/images/meat_lab.png',
              ),
              SizedBox(height: 40.h),

              Container(
                margin: EdgeInsets.fromLTRB(40.w, 0, 40.w, 40.h),
                child: MainButton(
                  onPressed: () async {
                    addProcessedMeatViewModel.clickedbutton(context, meatModel);
                  },
                  text: '완료',
                  width: double.infinity,
                  height: 104.h,
                  mode: 1,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

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
import 'package:structure/viewModel/data_management/researcher/data_add_processed_meat_view_model.dart';
import 'package:structure/components/main_button.dart';

class DataAddProcessedMeatScreen extends StatelessWidget {
  final MeatModel meatModel;
  const DataAddProcessedMeatScreen({super.key, required this.meatModel});

  @override
  Widget build(BuildContext context) {
    DataAddProcessedMeatViewModel addProcessedMeatViewModel =
        context.watch<DataAddProcessedMeatViewModel>();

    return Scaffold(
      appBar: const CustomAppBar(
        title: '추가 정보 입력',
        backButton: true,
        closeButton: false,
      ),
      body: ScrollConfiguration(
        behavior: CustomScroll(),
        child: SingleChildScrollView(
          child: Container(
            margin: EdgeInsets.symmetric(horizontal: 40.w),
            child: Column(
              children: [
                SizedBox(height: 24.h),

                // 처리육 단면 촬영
                StepCard(
                  mainText: '처리육 단면 촬영',
                  status: meatModel.imageCompleted ? 1 : 2,
                  imageUrl: 'assets/images/meat_image.png',
                  onTap: () => addProcessedMeatViewModel.clickedImage(context),
                ),
                SizedBox(height: 16.h),

                // 처리육 관능평가
                StepCard(
                  mainText: '처리육 관능평가',
                  status: meatModel.sensoryCompleted ? 1 : 2,
                  imageUrl: 'assets/images/meat_eval.png',
                  onTap: () =>
                      addProcessedMeatViewModel.clickedSensory(context),
                ),
                SizedBox(height: 16.h),

                // 처리육 전자혀
                StepCard(
                  mainText: '처리육 전자혀 데이터',
                  status: meatModel.tongueCompleted ? 1 : 2,
                  imageUrl: 'assets/images/meat_tongue.png',
                  onTap: () => addProcessedMeatViewModel.clickedTongue(context),
                ),
                SizedBox(height: 16.h),

                // 처리육 실험
                StepCard(
                  mainText: '처리육 실험 데이터',
                  status: meatModel.labCompleted ? 1 : 2,
                  imageUrl: 'assets/images/meat_lab.png',
                  onTap: () => addProcessedMeatViewModel.clickedLab(context),
                ),
                SizedBox(height: 16.h),

                // Divdier
                const CustomDivider(),
                SizedBox(height: 16.h),

                // 가열육 단면 촬영
                StepCard(
                  mainText: '가열육 단면 촬영',
                  status: meatModel.heatedImageCompleted ? 1 : 2,
                  imageUrl: 'assets/images/meat_image.png',
                  onTap: () =>
                      addProcessedMeatViewModel.clickedHeatedImage(context),
                ),
                SizedBox(height: 16.h),

                // 가열육 관능 평가
                StepCard(
                  mainText: '가열육 관능평가',
                  status: meatModel.heatedSensoryCompleted ? 1 : 2,
                  imageUrl: 'assets/images/meat_eval.png',
                  onTap: () =>
                      addProcessedMeatViewModel.clickedHeatedSensory(context),
                ),
                SizedBox(height: 16.h),

                // 가열육 전자혀
                StepCard(
                  mainText: '가열육 전자혀 데이터',
                  status: meatModel.heatedTongueCompleted ? 1 : 2,
                  imageUrl: 'assets/images/meat_tongue.png',
                  onTap: () =>
                      addProcessedMeatViewModel.clickedHeatedTongue(context),
                ),
                SizedBox(height: 16.h),

                // 가열육 실험 데이터
                StepCard(
                  mainText: '가열육 실험 데이터',
                  status: meatModel.heatedLabCompleted ? 1 : 2,
                  imageUrl: 'assets/images/meat_lab.png',
                  onTap: () =>
                      addProcessedMeatViewModel.clickedHeatedLab(context),
                ),
                SizedBox(height: 64.h),

                Container(
                  margin: EdgeInsets.only(bottom: 40.h),
                  child: MainButton(
                    width: double.infinity,
                    height: 96.h,
                    text: '완료',
                    onPressed: () async {
                      addProcessedMeatViewModel.clickedbutton(
                          context, meatModel);
                    },
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

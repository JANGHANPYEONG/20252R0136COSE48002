//
//
// 원육 추가 페이지(View) : Researcher
//
//

import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/custom_divider.dart';
import 'package:structure/components/custom_scroll.dart';
import 'package:structure/components/main_button.dart';
import 'package:structure/components/step_card.dart';
import 'package:structure/model/meat_model.dart';
import 'package:structure/viewModel/data_management/researcher/add_raw_meat_view_model.dart';

class DataAddRawMeatScreen extends StatelessWidget {
  final MeatModel meatModel;
  const DataAddRawMeatScreen({super.key, required this.meatModel});

  @override
  Widget build(BuildContext context) {
    AddRawMeatViewModel addRawMeatViewModel =
        context.watch<AddRawMeatViewModel>();

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
                // 원육 기본 정보 (수정 불가)
                StepCard(
                  mainText: '원육 기본정보',
                  status: 4, // 없음
                  imageUrl: 'assets/images/meat_info.png',
                  onTap: () => addRawMeatViewModel.clicekdBasic(context),
                ),
                SizedBox(height: 16.h),

                // 원육 단면 촬영 (수정 불가)
                StepCard(
                  mainText: '원육 단면 촬영',
                  status: 4, // 없음
                  imageUrl: 'assets/images/meat_image.png',
                  onTap: () => addRawMeatViewModel.clickedBasicImage(context),
                ),
                SizedBox(height: 16.h),

                // 원육 관능 평가 (수정 불가)
                StepCard(
                  mainText: '원육 관능평가',
                  status: 4, // 없음
                  imageUrl: 'assets/images/meat_eval.png',
                  onTap: () => addRawMeatViewModel.clicekdFresh(context),
                ),
                SizedBox(height: 16.h),

                // 원육 전자혀 데이터
                StepCard(
                  mainText: '원육 전자혀 데이터',
                  status: meatModel.tongueCompleted ? 1 : 2,
                  imageUrl: 'assets/images/meat_tongue.png',
                  onTap: () => addRawMeatViewModel.clickedTongue(context),
                ),
                SizedBox(height: 16.h),

                // 원육 실험 데이터
                StepCard(
                  mainText: '원육 실험 데이터',
                  status: meatModel.labCompleted ? 1 : 2,
                  imageUrl: 'assets/images/meat_lab.png',
                  onTap: () => addRawMeatViewModel.clickedLab(context),
                ),
                SizedBox(height: 16.h),

                // Divdier
                const CustomDivider(),
                SizedBox(height: 16.h),

                // 가열육 단면촬영 체크하는 변수 meatModel의 변수 추가하고 변경
                StepCard(
                  mainText: '가열육 단면 촬영',
                  status: meatModel.heatedImageCompleted ? 1 : 2,
                  imageUrl: 'assets/images/meat_image.png',
                  onTap: () => addRawMeatViewModel.clickedImage(context),
                ),
                SizedBox(height: 16.h),

                StepCard(
                  mainText: '가열육 관능평가',
                  status: meatModel.heatedSensoryCompleted ? 1 : 2,
                  imageUrl: 'assets/images/meat_eval.png',
                  onTap: () => addRawMeatViewModel.clickedHeated(context),
                ),
                SizedBox(height: 16.h),

                StepCard(
                  mainText: '가열육 전자혀 데이터',
                  status: meatModel.heatedTongueCompleted ? 1 : 2,
                  imageUrl: 'assets/images/meat_tongue.png',
                  onTap: () => addRawMeatViewModel.clickedHeatedTongue(context),
                ),
                SizedBox(height: 16.h),

                StepCard(
                  mainText: '가열육 실험 데이터',
                  status: meatModel.heatedLabCompleted ? 1 : 2,
                  imageUrl: 'assets/images/meat_lab.png',
                  onTap: () => addRawMeatViewModel.clickedHeatedLab(context),
                ),
                SizedBox(height: 64.h),

                Container(
                  margin: EdgeInsets.only(bottom: 40.h),
                  child: MainButton(
                    width: double.infinity,
                    height: 96.h,
                    text: '완료',
                    onPressed: () async {
                      addRawMeatViewModel.clickedbutton(context, meatModel);
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

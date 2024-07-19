//
//
// 처리육(딥에이징) 추가 페이지(View) : Researcher
//
//

import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/step_card.dart';
import 'package:structure/model/meat_model.dart';
import 'package:structure/viewModel/data_management/researcher/add_processed_meat_view_model.dart';
import 'package:structure/components/main_button.dart';

class AddProcessedMeatMainScreen extends StatefulWidget {
  final MeatModel meatModel;

  const AddProcessedMeatMainScreen({
    super.key,
    required this.meatModel,
  });

  @override
  State<AddProcessedMeatMainScreen> createState() =>
      _AddProcessedMeatMainScreenState();
}

class _AddProcessedMeatMainScreenState
    extends State<AddProcessedMeatMainScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: const CustomAppBar(
        title: '추가 정보 입력',
        backButton: true,
        closeButton: false,
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            SizedBox(height: 40.h),

            // 처리육 단면 촬영
            StepCard(
              mainText: '처리육 단면 촬영',
              status: widget.meatModel.deepAgedImageCompleted ? 1 : 2,
              onTap: () => context
                  .read<AddProcessedMeatViewModel>()
                  .clickedImage(context),
              imageUrl: 'assets/images/meat_image.png',
            ),

            SizedBox(height: 18.h),

            // 처리육 관능평가
            StepCard(
              mainText: '처리육 관능평가',
              status: widget.meatModel.deepAgedFreshCompleted ? 1 : 2,
              onTap: () => context
                  .read<AddProcessedMeatViewModel>()
                  .clickedEval(context),
              imageUrl: 'assets/images/meat_eval.png',
            ),
            SizedBox(height: 18.h),

            // 처리육 전자혀
            StepCard(
              mainText: '처리육 전자혀 데이터',
              status: widget.meatModel.tongueCompleted ? 1 : 2,
              onTap: () => context
                  .read<AddProcessedMeatViewModel>()
                  .clickedTongue(context),
              imageUrl: 'assets/images/meat_tongue.png',
            ),

            SizedBox(height: 18.h),

            // 처리육 실험
            StepCard(
              mainText: '처리육 실험 데이터',
              status: widget.meatModel.labCompleted ? 1 : 2,
              onTap: () =>
                  context.read<AddProcessedMeatViewModel>().clickedLab(context),
              imageUrl: 'assets/images/meat_lab.png',
            ),

            SizedBox(height: 18.h),

            // Divdier
            Container(
              margin: EdgeInsets.symmetric(horizontal: 16.w),
              child: const Divider(
                color: Color.fromARGB(255, 155, 155, 155),
                thickness: 1,
              ),
            ),

            // 가열육 단면 촬영
            StepCard(
              mainText: '가열육 단면 촬영',
              status: widget.meatModel.deepAgedImageCompleted ? 1 : 2,
              onTap: () => context
                  .read<AddProcessedMeatViewModel>()
                  .clickedImage(context),
              imageUrl: 'assets/images/meat_image.png',
            ),

            SizedBox(height: 18.h),

            // 가열육 관능 평가
            StepCard(
              mainText: '가열육 관능평가',
              status: widget.meatModel.heatedCompleted ? 1 : 2,
              onTap: () => context
                  .read<AddProcessedMeatViewModel>()
                  .clickedHeatedEval(context),
              imageUrl: 'assets/images/meat_eval.png',
            ),

            SizedBox(height: 18.h),

            // 가열육 전자혀
            StepCard(
              mainText: '가열육 전자혀 데이터',
              status: widget.meatModel.tongueCompleted ? 1 : 2,
              onTap: () => context
                  .read<AddProcessedMeatViewModel>()
                  .clickedTongue(context),
              imageUrl: 'assets/images/meat_tongue.png',
            ),

            SizedBox(height: 18.h),

            // 가열육 실험 데이터
            StepCard(
              mainText: '가열육 실험 데이터',
              status: widget.meatModel.labCompleted ? 1 : 2,
              onTap: () =>
                  context.read<AddProcessedMeatViewModel>().clickedLab(context),
              imageUrl: 'assets/images/meat_lab.png',
            ),

            SizedBox(height: 40.h),

            Container(
              margin: EdgeInsets.only(bottom: 40.h),
              child: MainButton(
                onPressed: () async {
                  context
                      .read<AddProcessedMeatViewModel>()
                      .clickedbutton(context, widget.meatModel);
                },
                text: '완료',
                width: 658.w,
                height: 104.h,
                mode: 1,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

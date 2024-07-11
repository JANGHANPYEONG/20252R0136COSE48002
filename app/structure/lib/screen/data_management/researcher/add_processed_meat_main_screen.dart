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
import 'package:structure/main.dart';
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
      body: Center(
        child: Column(
          children: [
            SizedBox(height: 48.h),
            InkWell(
              onTap: () => context
                  .read<AddProcessedMeatViewModel>()
                  .clickedImage(context),
              child: StepCard(
                mainText: '처리육 단면 촬영',
                status: meatModel.deepAgedImageCompleted ? 1 : 2,
                // isCompleted: meatModel.deepAgedImageCompleted,
                // isBefore: false,
                imageUrl: 'assets/images/meat_image.png',
              ),
            ),
            SizedBox(height: 18.h),
            InkWell(
              onTap: () => widget.meatModel.deepAgedImageCompleted
                  ? context
                      .read<AddProcessedMeatViewModel>()
                      .clickedProcessedEval(context)
                  : null,
              child: StepCard(
                mainText: '처리육 관능평가',
                status: widget.meatModel.deepAgedImageCompleted
                    ? widget.meatModel.deepAgedFreshCompleted
                        ? 1
                        : 2
                    : 0,
                // isCompleted: widget.meatModel.deepAgedFreshCompleted,
                // isBefore: !widget.meatModel.deepAgedImageCompleted,
                imageUrl: 'assets/images/meat_eval.png',
              ),
            ),
            SizedBox(
              height: 18.h,
            ),
            InkWell(
              onTap: () => context
                  .read<AddProcessedMeatViewModel>()
                  .clickedHeatedEval(context),
              child: StepCard(
                mainText: '가열육 관능평가',
                status: widget.meatModel.heatedCompleted ? 1 : 2,
                // isCompleted: widget.meatModel.heatedCompleted,
                // isBefore: false,
                imageUrl: 'assets/images/meat_eval.png',
              ),
            ),
            SizedBox(
              height: 18.h,
            ),
            InkWell(
              onTap: () => context
                  .read<AddProcessedMeatViewModel>()
                  .clickedTongue(context),
              child: StepCard(
                mainText: '전자혀 데이터',
                status: widget.meatModel.tongueCompleted ? 1 : 2,
                // isCompleted: widget.meatModel.tongueCompleted,
                // isBefore: false,
                imageUrl: 'assets/images/meat_tongue.png',
              ),
            ),
            SizedBox(
              height: 18.h,
            ),
            InkWell(
              onTap: () =>
                  context.read<AddProcessedMeatViewModel>().clickedLab(context),
              child: StepCard(
                mainText: '실험 데이터',
                status: widget.meatModel.labCompleted ? 1 : 2,
                // isCompleted: widget.meatModel.labCompleted,
                // isBefore: false,
                imageUrl: 'assets/images/meat_lab.png',
              ),
            ),
            const Spacer(),
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

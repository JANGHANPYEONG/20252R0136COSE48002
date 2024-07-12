//
//
// 원육 추가 페이지(View) : Researcher
//
//

import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/main_button.dart';
import 'package:structure/components/step_card.dart';
import 'package:structure/model/meat_model.dart';
import 'package:structure/viewModel/data_management/normal/edit_meat_data_view_model.dart';
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
      body: SingleChildScrollView(
        child: Stack(
          children: [
            Column(
              children: [
                // 육류 기본 정보
                InkWell(
                  onTap: () =>
                      context.read<AddRawMeatViewModel>().clicekdBasic(context),
                  child: const StepCard(
                    mainText: '육류 기본정보',
                    status: 4, // 없음
                    imageUrl: 'assets/images/meat_info.png',
                  ),
                ),
                SizedBox(height: 10.h),

                // 육류 단면 촬영
                InkWell(
                  onTap: () => context
                      .read<AddRawMeatViewModel>()
                      .clickedBasicImage(context),
                  child: const StepCard(
                    mainText: '육류 단면 촬영',
                    status: 4, // 없음
                    // isEditable: context.read<EditMeatDataViewModel>().isEditable,
                    imageUrl: 'assets/images/meat_image.png',
                  ),
                ),
                SizedBox(height: 10.h),

                // 신선육 관능 평가
                InkWell(
                  onTap: () =>
                      context.read<AddRawMeatViewModel>().clicekdFresh(context),
                  child: const StepCard(
                    mainText: '신선육 관능평가',
                    status: 4, // 없음
                    imageUrl: 'assets/images/meat_eval.png',
                  ),
                ),
                SizedBox(
                  height: 10.h,
                ),
                InkWell(
                  onTap: () => context
                      .read<AddRawMeatViewModel>()
                      .clickedTongue(context),
                  child: StepCard(
                    mainText: '원육 전자혀 데이터',
                    status: meatModel.tongueCompleted ? 1 : 2,
                    // isCompleted: meatModel.tongueCompleted,
                    // isBefore: false,
                    imageUrl: 'assets/images/meat_tongue.png',
                  ),
                ),
                SizedBox(
                  height: 10.h,
                ),
                InkWell(
                  onTap: () =>
                      context.read<AddRawMeatViewModel>().clickedLab(context),
                  child: StepCard(
                    mainText: '원육 실험 데이터',
                    status: meatModel.labCompleted ? 1 : 2,
                    // isCompleted: meatModel.labCompleted,
                    // isBefore: false,
                    imageUrl: 'assets/images/meat_lab.png',
                  ),
                ),
                SizedBox(
                  height: 10.h,
                ),
                Container(
                  margin: EdgeInsets.symmetric(horizontal: 16.w),
                  child: const Divider(
                    color: Color.fromARGB(255, 155, 155, 155),
                    thickness: 1,
                  ),
                ),
                InkWell(
                  onTap: () =>
                      context.read<AddRawMeatViewModel>().clickedImage(context),
                  child: StepCard(
                    mainText: '가열육 단면 촬영',
                    //가열육 단면촬영 체크하는 변수 meatModel의 변수 추가하고 변경
                    status: meatModel.deepAgedImageCompleted ? 1 : 2,
                    // isCompleted: meatModel.deepAgedImageCompleted,
                    // isBefore: false,
                    imageUrl: 'assets/images/meat_image.png',
                  ),
                ),
                InkWell(
                  onTap: () => context
                      .read<AddRawMeatViewModel>()
                      .clickedHeated(context),
                  child: StepCard(
                    mainText: '가열육 관능평가',
                    status: meatModel.heatedCompleted ? 1 : 2,
                    // isCompleted: meatModel.heatedCompleted,
                    // isBefore: false,
                    imageUrl: 'assets/images/meat_eval.png',
                  ),
                ),
                SizedBox(
                  height: 10.h,
                ),
                InkWell(
                  onTap: () => context
                      .read<AddRawMeatViewModel>()
                      .clickedTongue(context),
                  child: StepCard(
                    mainText: '가열육 전자혀 데이터',
                    status: meatModel.tongueCompleted ? 1 : 2,
                    // isCompleted: meatModel.tongueCompleted,
                    // isBefore: false,
                    imageUrl: 'assets/images/meat_tongue.png',
                  ),
                ),
                SizedBox(
                  height: 10.h,
                ),
                InkWell(
                  onTap: () =>
                      context.read<AddRawMeatViewModel>().clickedLab(context),
                  child: StepCard(
                    mainText: '가열육 실험 데이터',
                    status: meatModel.labCompleted ? 1 : 2,
                    imageUrl: 'assets/images/meat_lab.png',
                  ),
                ),
                Container(
                  margin: EdgeInsets.only(bottom: 20.h),
                  child: MainButton(
                    onPressed: () async {
                      context
                          .read<AddRawMeatViewModel>()
                          .clickedbutton(context, meatModel);
                    },
                    text: '완료',
                    width: 658.w,
                    height: 104.h,
                    mode: 1,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

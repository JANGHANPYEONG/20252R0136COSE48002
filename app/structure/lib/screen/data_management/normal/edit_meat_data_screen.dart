//
//
// 육류 등록 수정 | 확인 페이지(View) : Normal
//
//
import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/step_card.dart';
import 'package:structure/viewModel/data_management/normal/edit_meat_data_view_model.dart';

class EditMeatDataScreen extends StatelessWidget {
  const EditMeatDataScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: CustomAppBar(
          title: '${context.read<EditMeatDataViewModel>().meatModel.id}',
          backButton: true,
          closeButton: false),
      body: Center(
        child: Column(
          children: [
            SizedBox(height: 48.h),

            // 육류 기본 정보
            InkWell(
              onTap: () =>
                  context.read<EditMeatDataViewModel>().clicekdBasic(context),
              child: StepCard2(
                mainText: '육류 기본정보',
                isEditable: context.read<EditMeatDataViewModel>().isEditable,
                imageUrl: 'assets/images/meat_info.png',
              ),
            ),
            SizedBox(height: 18.h),

            // 육류 단면 촬영
            InkWell(
              onTap: () =>
                  context.read<EditMeatDataViewModel>().clickedImage(context),
              child: StepCard2(
                mainText: '육류 단면 촬영',
                isEditable: context.read<EditMeatDataViewModel>().isEditable,
                imageUrl: 'assets/images/meat_image.png',
              ),
            ),
            SizedBox(height: 18.h),

            // 신선육 관능 평가
            InkWell(
              onTap: () =>
                  context.read<EditMeatDataViewModel>().clicekdFresh(context),
              child: StepCard2(
                mainText: '신선육 관능평가',
                isEditable: context.read<EditMeatDataViewModel>().isEditable,
                imageUrl: 'assets/images/meat_eval.png',
              ),
            ),
          ],
        ),
      ),
    );
  }
}

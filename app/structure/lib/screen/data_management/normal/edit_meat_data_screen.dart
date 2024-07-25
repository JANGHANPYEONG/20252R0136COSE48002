//
//
// 육류 등록 수정 | 확인 페이지(View) : Normal
//
//
import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/loading_screen.dart';
import 'package:structure/components/round_button.dart';
import 'package:structure/components/step_card.dart';
import 'package:structure/config/pallete.dart';
import 'package:structure/viewModel/data_management/normal/edit_meat_data_view_model.dart';

class EditMeatDataScreen extends StatelessWidget {
  const EditMeatDataScreen({super.key});

  @override
  Widget build(BuildContext context) {
    EditMeatDataViewModel editMeatDataViewModel =
        context.watch<EditMeatDataViewModel>();

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: CustomAppBar(
          title: '${editMeatDataViewModel.meatModel.meatId}',
          backButton: true,
          closeButton: false),
      body: Stack(
        children: [
          Column(
            children: [
              SizedBox(height: 48.h),

              // 육류 기본 정보
              StepCard(
                mainText: '육류 기본정보',
                status: editMeatDataViewModel.isNormal
                    ? editMeatDataViewModel.isEditable
                        ? 3 // 수정 가능
                        : 4 // 수정 불가
                    : null, // 없음

                onTap: () => editMeatDataViewModel.clicekdBasic(context),
                imageUrl: 'assets/images/meat_info.png',
              ),
              SizedBox(height: 18.h),

              // 육류 단면 촬영
              StepCard(
                mainText: '육류 단면 촬영',
                status: editMeatDataViewModel.isNormal
                    ? editMeatDataViewModel.isEditable
                        ? 3 // 수정 가능
                        : 4 // 수정 불가
                    : null, // 없음
                onTap: () => editMeatDataViewModel.clickedImage(context),
                imageUrl: 'assets/images/meat_image.png',
              ),

              SizedBox(height: 18.h),

              // 신선육 관능 평가
              StepCard(
                mainText: '원육 관능평가',
                status: editMeatDataViewModel.isNormal
                    ? editMeatDataViewModel.isEditable
                        ? 3 // 수정 가능
                        : 4 // 수정 불가
                    : null, // 없음
                onTap: () => editMeatDataViewModel.clicekdFresh(context),
                imageUrl: 'assets/images/meat_eval.png',
              ),

              const Spacer(),

              // 연구자 신분 + 승인되지 않은 데이터일때만
              if (editMeatDataViewModel.showAcceptBtn())
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    RoundButton(
                      onPress: () {
                        editMeatDataViewModel.rejectMeatData(context);
                      },
                      text: Text('반려', style: Palette.fieldPlaceHolderWhite),
                      bgColor: Palette.alertColor,
                      width: 310.w,
                      height: 96.h,
                    ),
                    SizedBox(width: 20.w),
                    RoundButton(
                      onPress: () {
                        editMeatDataViewModel.acceptMeatData(context);
                      },
                      text: Text('승인', style: Palette.fieldPlaceHolderWhite),
                      bgColor: Palette.checkSpeciesColor,
                      width: 310.w,
                      height: 96.h,
                    ),
                  ],
                ),

              SizedBox(height: 40.h),
            ],
          ),
          editMeatDataViewModel.isLoading
              ? const Center(child: LoadingScreen())
              : Container(),
        ],
      ),
    );
  }
}

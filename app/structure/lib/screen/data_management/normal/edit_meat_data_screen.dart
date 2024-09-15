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
import 'package:structure/config/palette.dart';
import 'package:structure/viewModel/data_management/normal/edit_meat_data_view_model.dart';

class EditMeatDataScreen extends StatelessWidget {
  const EditMeatDataScreen({super.key});

  @override
  Widget build(BuildContext context) {
    EditMeatDataViewModel editMeatDataViewModel =
        context.watch<EditMeatDataViewModel>();

    return Scaffold(
      appBar: CustomAppBar(title: '${editMeatDataViewModel.meatModel.meatId}'),
      body: Stack(
        children: [
          Container(
            margin: EdgeInsets.symmetric(horizontal: 40.w),
            child: Column(
              children: [
                SizedBox(height: 24.h),

                // 육류 기본 정보
                StepCard(
                  mainText: '육류 기본정보',
                  status: editMeatDataViewModel.isNormal
                      ? editMeatDataViewModel.isEditable
                          ? 3 // 수정 가능
                          : 4 // 수정 불가
                      : null, // 없음

                  onTap: () => editMeatDataViewModel.clicekdBasic(),
                  imageUrl: 'assets/images/meat_info.png',
                ),
                SizedBox(height: 16.h),

                // 육류 단면 촬영
                StepCard(
                  mainText: '육류 단면 촬영',
                  status: editMeatDataViewModel.isNormal
                      ? editMeatDataViewModel.isEditable
                          ? 3 // 수정 가능
                          : 4 // 수정 불가
                      : null, // 없음
                  onTap: () => editMeatDataViewModel.clickedImage(),
                  imageUrl: 'assets/images/meat_image.png',
                ),

                SizedBox(height: 16.h),

                // 원육 관능 평가
                StepCard(
                  mainText: '원육 관능평가',
                  status: editMeatDataViewModel.isNormal
                      ? editMeatDataViewModel.isEditable
                          ? 3 // 수정 가능
                          : 4 // 수정 불가
                      : null, // 없음
                  onTap: () => editMeatDataViewModel.clicekdFresh(),
                  imageUrl: 'assets/images/meat_eval.png',
                ),

                const Spacer(),

                // 연구자 신분 + 승인되지 않은 데이터일때만
                if (editMeatDataViewModel.showAcceptBtn())
                  Container(
                    margin: EdgeInsets.only(bottom: 40.h),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        // 반려 버튼
                        Expanded(
                          child: RoundButton(
                            onPress: () {
                              editMeatDataViewModel.rejectMeatData(context);
                            },
                            text: Text(
                              '반려',
                              style: Palette.h4Regular
                                  .copyWith(color: Colors.white),
                            ),
                            bgColor: Palette.error,
                            width: double.infinity,
                            height: 96.h,
                          ),
                        ),
                        SizedBox(width: 16.w),

                        // 승인 버튼
                        Expanded(
                          child: RoundButton(
                            onPress: () {
                              editMeatDataViewModel.acceptMeatData(context);
                            },
                            text: Text(
                              '승인',
                              style: Palette.h4Regular
                                  .copyWith(color: Colors.white),
                            ),
                            bgColor: Palette.primary,
                            width: double.infinity,
                            height: 96.h,
                          ),
                        ),
                      ],
                    ),
                  ),
              ],
            ),
          ),
          editMeatDataViewModel.isLoading
              ? const Center(child: LoadingScreen())
              : Container(),
        ],
      ),
    );
  }
}

//
//
// 육류 등록 페이지(View)
//
//

import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/custom_text_button.dart';
import 'package:structure/components/loading_screen.dart';
import 'package:structure/components/step_card.dart';
import 'package:structure/config/palette.dart';
import 'package:structure/model/meat_model.dart';
import 'package:structure/viewModel/meat_registration/meat_registration_view_model.dart';
import 'package:structure/components/main_button.dart';

class MeatRegistrationScreen extends StatefulWidget {
  final MeatModel meatModel;
  const MeatRegistrationScreen({
    super.key,
    required this.meatModel,
  });

  @override
  State<MeatRegistrationScreen> createState() => _MeatRegistrationScreenState();
}

class _MeatRegistrationScreenState extends State<MeatRegistrationScreen> {
  @override
  void initState() {
    super.initState();
    context.read<MeatRegistrationViewModel>().initialize(context);
  }

  @override
  Widget build(BuildContext context) {
    MeatRegistrationViewModel meatRegistrationViewModel =
        context.watch<MeatRegistrationViewModel>();

    return Scaffold(
      appBar: const CustomAppBar(title: '육류 등록'),
      body: Stack(
        children: [
          Container(
            margin: EdgeInsets.symmetric(horizontal: 40.w),
            child: Column(
              children: [
                SizedBox(height: 24.h),

                // STEP 1 : 육류 기본정보 등록
                StepCard(
                  mainText: '육류 기본정보',
                  status: widget.meatModel.basicCompleted ? 1 : 2,
                  onTap: () => meatRegistrationViewModel.clickedBasic(context),
                  imageUrl: 'assets/images/meat_info.png',
                ),
                SizedBox(height: 16.h),

                // STEP 2 : 육류 단면 촬영
                StepCard(
                  mainText: '육류 단면 촬영',
                  status: widget.meatModel.imageCompleted ? 1 : 2,
                  onTap: () => meatRegistrationViewModel.clickedImage(context),
                  imageUrl: 'assets/images/meat_image.png',
                ),
                SizedBox(height: 16.h),

                // STEP 3 : 원육 관능평가
                StepCard(
                  mainText: '원육 관능평가',
                  status: widget.meatModel.sensoryCompleted ? 1 : 2,
                  onTap: () =>
                      meatRegistrationViewModel.clickedFreshmeat(context),
                  imageUrl: 'assets/images/meat_eval.png',
                ),

                // 하단 완료 버튼
                if (meatRegistrationViewModel.checkAllCompleted())
                  Expanded(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text('육류 등록 완료!', style: Palette.h1),
                        SizedBox(height: 16.h),
                        Text('등록한 정보로 관리번호를 생성할 수 있어요.',
                            style: Palette.h5Secondary),
                        SizedBox(height: 48.h),

                        // 관리번호 생성 버튼
                        MainButton(
                          width: 280.w,
                          height: 96.h,
                          text: '관리번호 생성',
                          style:
                              Palette.h4Regular.copyWith(color: Colors.white),
                          onPressed: () async =>
                              meatRegistrationViewModel.clickCreateBtn(context),
                        ),
                        SizedBox(height: 24.h),

                        // 임시저장 버튼
                        CustomTextButton(
                          title: '임시저장 하기',
                          onPressed: () {
                            meatRegistrationViewModel
                                .clickedTempSaveButton(context);
                          },
                        ),
                      ],
                    ),
                  ),
              ],
            ),
          ),
          meatRegistrationViewModel.isLoading
              ? const Center(child: LoadingScreen())
              : Container(),
        ],
      ),
    );
  }
}

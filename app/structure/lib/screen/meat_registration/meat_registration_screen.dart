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
import 'package:structure/config/pallete.dart';
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
      backgroundColor: Colors.white,
      appBar: const CustomAppBar(
        title: '육류 등록',
        backButton: true,
        closeButton: false,
      ),
      body: Center(
        child: meatRegistrationViewModel.isLoading
            ? const LoadingScreen()
            : Column(
                children: [
                  SizedBox(height: 55.h),

                  // STEP 1 : 육류 기본정보 등록
                  StepCard(
                    mainText: '육류 기본정보',
                    status: widget.meatModel.basicCompleted ? 1 : 2,
                    onTap: () =>
                        meatRegistrationViewModel.clickedBasic(context),
                    imageUrl: 'assets/images/meat_info.png',
                  ),
                  SizedBox(height: 8.h),

                  // STEP 2 : 육류 단면 촬영
                  StepCard(
                    mainText: '육류 단면 촬영',
                    status: widget.meatModel.imageCompleted ? 1 : 2,
                    onTap: () =>
                        meatRegistrationViewModel.clickedImage(context),
                    imageUrl: 'assets/images/meat_image.png',
                  ),
                  SizedBox(height: 8.h),

                  // STEP 3 : 원육 관능평가
                  StepCard(
                    mainText: '원육 관능평가',
                    status: widget.meatModel.sensoryCompleted ? 1 : 2,
                    onTap: () =>
                        meatRegistrationViewModel.clickedFreshmeat(context),
                    imageUrl: 'assets/images/meat_eval.png',
                  ),
                  SizedBox(height: 116.h),

                  // 하단 완료 버튼
                  if (meatRegistrationViewModel.checkAllCompleted())
                    Column(
                      children: [
                        Text('육류 등록 완료!', style: Pallete.h1),
                        SizedBox(height: 12.h),
                        Text('등록한 정보로 관리번호를 생성할 수 있어요.', style: Pallete.h5Grey),
                        SizedBox(height: 50.h),

                        // 관리번호 생성 버튼
                        MainButton(
                          onPressed: () async =>
                              meatRegistrationViewModel.clickCreateBtn(context),
                          text: '관리번호 생성',
                          width: 282.w,
                          height: 96.h,
                          mode: 1,
                          style: Pallete.fieldPlaceHolderWhite,
                        ),
                        SizedBox(height: 22.h),

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
                ],
              ),
      ),
    );
  }
}

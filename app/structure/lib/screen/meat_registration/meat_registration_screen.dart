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
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: const CustomAppBar(
        title: '육류 등록',
        backButton: true,
        closeButton: false,
      ),
      body: Center(
        child: context.watch<MeatRegistrationViewModel>().isLoading
            ? const LoadingScreen()
            : Column(
                children: [
                  SizedBox(height: 55.h),

                  // STEP 1 : 육류 기본정보 등록
                  InkWell(
                    onTap: () => context
                        .read<MeatRegistrationViewModel>()
                        .clickedBasic(context),
                    child: StepCard(
                      mainText: '육류 기본정보',
                      status: widget.meatModel.basicCompleted ? 1 : 2,
                      // isCompleted: widget.meatModel.basicCompleted,
                      // isBefore: false,
                      imageUrl: 'assets/images/meat_info.png',
                    ),
                  ),
                  SizedBox(height: 4.h),
                  Padding(
                    padding: EdgeInsets.symmetric(horizontal: 40.w),
                    child: const Divider(
                      thickness: 1,
                    ),
                  ),
                  SizedBox(height: 4.h),

                  // STEP 2 : 육류 단면 촬영
                  InkWell(
                      onTap: () => widget.meatModel.basicCompleted
                          ? context
                              .read<MeatRegistrationViewModel>()
                              .clickedImage(context)
                          : null,
                      child: StepCard(
                        mainText: '육류 단면 촬영',
                        status: widget.meatModel.freshImageCompleted ? 1 : 2,
                        // isCompleted: widget.meatModel.freshImageCompleted,
                        // isBefore: false,
                        imageUrl: 'assets/images/meat_image.png',
                      )),
                  SizedBox(height: 4.h),
                  Padding(
                    padding: EdgeInsets.symmetric(horizontal: 40.w),
                    child: const Divider(
                      thickness: 1,
                    ),
                  ),
                  SizedBox(height: 4.h),

                  // STEP 3 : 신선육 관능평가
                  InkWell(
                      onTap: () => widget.meatModel.freshImageCompleted
                          ? context
                              .read<MeatRegistrationViewModel>()
                              .clickedFreshmeat(context)
                          : null,
                      child: StepCard(
                        mainText: '신선육 관능평가',
                        status: widget.meatModel.rawFreshCompleted ? 1 : 2,
                        // isCompleted: widget.meatModel.rawFreshCompleted,
                        // isBefore: false,
                        imageUrl: 'assets/images/meat_eval.png',
                      )),
                  SizedBox(height: 116.h),

                  // 하단 완료 버튼
                  if (widget.meatModel.basicCompleted &&
                      widget.meatModel.freshImageCompleted &&
                      widget.meatModel.rawFreshCompleted)
                    Column(
                      children: [
                        Text('육류 등록 완료!', style: Palette.h1),
                        SizedBox(height: 12.h),
                        Text('등록한 정보로 관리번호를 생성할 수 있어요.', style: Palette.h5Grey),
                        SizedBox(height: 50.h),

                        // 관리번호 생성 버튼
                        MainButton(
                          onPressed: () async {
                            context
                                .read<MeatRegistrationViewModel>()
                                .clickCreateBtn(context);
                          },
                          text: '관리번호 만들기',
                          width: 282.w,
                          height: 96.h,
                          mode: 1,
                          style: Palette.fieldPlaceHolderWhite,
                        ),
                        SizedBox(height: 22.h),

                        // 임시저장 버튼
                        CustomTextButton(
                          title: '임시저장 하기',
                          onPressed: () async =>
                              context.read<MeatRegistrationViewModel>(),
                        ),
                      ],
                    ),
                ],
              ),
      ),
    );
  }
}

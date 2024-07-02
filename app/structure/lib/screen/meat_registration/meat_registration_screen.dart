//
//
// 육류 등록 페이지(View)
//
//

import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/step_card.dart';
import 'package:structure/config/pallete.dart';
import 'package:structure/model/meat_model.dart';
import 'package:structure/viewModel/meat_registration/meat_registration_view_model.dart';

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
            ? const CircularProgressIndicator()
            : Column(
                children: [
                  SizedBox(
                    height: 55.h,
                  ),
                  // STEP 1 : 육류 기본정보 등록
                  InkWell(
                    onTap: () => context
                        .read<MeatRegistrationViewModel>()
                        .clickedBasic(context),
                    child: StepCard(
                      mainText: '육류 기본정보',
                      isCompleted: widget.meatModel.basicCompleted,
                      isBefore: false,
                      imageUrl: 'assets/images/meat_info.png',
                    ),
                  ),
                  SizedBox(
                    height: 4.h,
                  ),
                  Padding(
                    padding: EdgeInsets.symmetric(horizontal: 40.w),
                    child: const Divider(
                      thickness: 1,
                    ),
                  ),
                  SizedBox(
                    height: 4.h,
                  ),
                  // STEP 2 : 육류 단면 촬영
                  InkWell(
                      onTap: () => widget.meatModel.basicCompleted
                          ? context
                              .read<MeatRegistrationViewModel>()
                              .clickedImage(context)
                          : null,
                      child: StepCard(
                        mainText: '육류 단면 촬영',
                        isCompleted: widget.meatModel.freshImageCompleted,
                        isBefore: false,
                        imageUrl: 'assets/images/meat_image.png',
                      )),
                  SizedBox(
                    height: 4.h,
                  ),
                  Padding(
                    padding: EdgeInsets.symmetric(horizontal: 40.w),
                    child: const Divider(
                      thickness: 1,
                    ),
                  ),
                  SizedBox(
                    height: 4.h,
                  ),
                  // STEP 3 : 신선육 관능평가
                  InkWell(
                      onTap: () => widget.meatModel.freshImageCompleted
                          ? context
                              .read<MeatRegistrationViewModel>()
                              .clickedFreshmeat(context)
                          : null,
                      child: StepCard(
                        mainText: '신선육 관능평가',
                        isCompleted: widget.meatModel.rawFreshCompleted,
                        isBefore: false,
                        imageUrl: 'assets/images/meat_eval.png',
                      )),
                  const Spacer(),
                  Container(
                    margin: EdgeInsets.only(bottom: 28.h),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        SizedBox(
                          width: 310.w,
                          height: 104.h,
                          // 임시 저장 버튼
                          child: ElevatedButton(
                            onPressed: widget.meatModel.basicCompleted
                                ? () async => context
                                    .read<MeatRegistrationViewModel>()
                                    .clickedTempSaveButton(context)
                                : null,
                            style: ElevatedButton.styleFrom(
                                disabledBackgroundColor: Palette.notEditableBg,
                                backgroundColor: Palette.mainBtnAtvBg,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(20.sp),
                                ),
                                elevation: 0),
                            child: Center(
                              child: Text('임시저장', style: Palette.mainBtnTitle),
                            ),
                          ),
                        ),
                        SizedBox(
                          width: 32.w,
                        ),
                        // 관리 번호 생성 버튼
                        SizedBox(
                          width: 310.w,
                          height: 104.h,
                          child: ElevatedButton(
                            onPressed: widget.meatModel.basicCompleted &&
                                    widget.meatModel.freshImageCompleted &&
                                    widget.meatModel.rawFreshCompleted
                                ? () => context
                                    .read<MeatRegistrationViewModel>()
                                    .clickedSaveButton(context)
                                : null,
                            style: ElevatedButton.styleFrom(
                                disabledBackgroundColor: Palette.notEditableBg,
                                backgroundColor: Palette.mainBtnAtvBg,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(20.sp),
                                ),
                                elevation: 0),
                            child: Center(
                              child: Text('저장', style: Palette.mainBtnTitle),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
      ),
    );
  }
}

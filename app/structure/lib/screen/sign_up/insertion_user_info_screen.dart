import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/custom_divider.dart';
import 'package:structure/components/custom_pop_up.dart';
import 'package:structure/components/main_button.dart';
import 'package:structure/components/main_input_field.dart';
import 'package:structure/config/palette.dart';
import 'package:structure/viewModel/sign_up/insertion_user_info_view_model.dart';
import 'package:structure/components/loading_screen.dart';

class InsertionUserInfoScreen extends StatefulWidget {
  const InsertionUserInfoScreen({super.key});

  @override
  State<InsertionUserInfoScreen> createState() =>
      _InsertionUserInfoScreenState();
}

class _InsertionUserInfoScreenState extends State<InsertionUserInfoScreen> {
  late InsertionUserInfoViewModel insertionUserInfoViewModel;

  @override
  void initState() {
    super.initState();
    insertionUserInfoViewModel = context.read<InsertionUserInfoViewModel>();
    insertionUserInfoViewModel.email.addListener(_validateInput);
  }

  @override
  void dispose() {
    insertionUserInfoViewModel.email.removeListener(_validateInput);
    super.dispose();
  }

  void _validateInput() {
    setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const CustomAppBar(
        backButton: true,
        closeButton: false,
        title: '회원가입',
      ),
      body: GestureDetector(
        onTap: () => FocusScope.of(context).unfocus(),
        child: Stack(
          children: [
            SingleChildScrollView(
              child: Form(
                key: context.read<InsertionUserInfoViewModel>().formKey,
                child: Container(
                  margin: EdgeInsets.symmetric(horizontal: 40.w),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      SizedBox(height: 24.h),

                      // 이름
                      Text('이름', style: Palette.h5SemiBoldSecondary),
                      SizedBox(height: 16.h),

                      MainInputField(
                        width: double.infinity,
                        controller:
                            context.read<InsertionUserInfoViewModel>().name,
                        onChangeFunc: (value) => context
                            .read<InsertionUserInfoViewModel>()
                            .nameCheck(value),
                      ),
                      SizedBox(height: 32.h),

                      // 이메일
                      Text('이메일', style: Palette.h5SemiBoldSecondary),
                      SizedBox(height: 16.h),

                      Stack(
                        children: [
                          // 이메일 입력 필드
                          MainInputField(
                            width: double.infinity,
                            formKey: context
                                .read<InsertionUserInfoViewModel>()
                                .formKey,
                            controller: context
                                .read<InsertionUserInfoViewModel>()
                                .email,
                            validateFunc: (value) => context
                                .read<InsertionUserInfoViewModel>()
                                .idValidate(value),
                            onChangeFunc: (value) => context
                                .read<InsertionUserInfoViewModel>()
                                .onChangeEmail(value),
                            contentPadding:
                                EdgeInsets.only(left: 24.w, right: 200.w),
                          ),

                          // 중복확인 버튼
                          Positioned(
                            right: 24.w,
                            child: TextButton(
                              onPressed: context
                                      .watch<InsertionUserInfoViewModel>()
                                      .isUnique
                                  ? null
                                  : () => context
                                          .read<InsertionUserInfoViewModel>()
                                          .isValidId
                                      ? context
                                          .read<InsertionUserInfoViewModel>()
                                          .dupliCheck(context)
                                      : null,
                              child: context
                                      .read<InsertionUserInfoViewModel>()
                                      .isUnique
                                  ? const Icon(
                                      Icons.check,
                                      color: Palette.primary,
                                    )
                                  : Text('중복확인', style: Palette.h4Regular),
                            ),
                          ),
                        ],
                      ),
                      SizedBox(height: 36.h),

                      // 비밀번호
                      Text('비밀번호', style: Palette.h5SemiBoldSecondary),
                      SizedBox(height: 16.h),

                      // 비밀번호 입력 필드
                      MainInputField(
                        width: double.infinity,
                        formKey:
                            context.read<InsertionUserInfoViewModel>().formKey,
                        obscureText: true,
                        controller:
                            context.read<InsertionUserInfoViewModel>().password,
                        validateFunc: (value) => context
                            .read<InsertionUserInfoViewModel>()
                            .pwValidate(value),
                        hintText: '영문 대/소문자+숫자+특수문자',
                      ),
                      SizedBox(height: 16.h),

                      // 비밀번호 확인
                      MainInputField(
                        width: double.infinity,
                        formKey:
                            context.read<InsertionUserInfoViewModel>().formKey,
                        obscureText: true,
                        controller: context
                            .read<InsertionUserInfoViewModel>()
                            .cPassword,
                        validateFunc: (value) => context
                            .read<InsertionUserInfoViewModel>()
                            .cPwValidate(value),
                        hintText: '비밀번호 확인',
                      ),
                      SizedBox(height: 32.h),

                      // 약관 동의
                      Container(
                        decoration: BoxDecoration(
                          border: Border.all(color: Palette.onPrimary),
                          borderRadius: BorderRadius.circular(20.r),
                        ),
                        width: double.infinity,
                        child: Column(
                          children: [
                            // 약관 전체 동의
                            Row(
                              children: [
                                Checkbox(
                                  value: context
                                      .watch<InsertionUserInfoViewModel>()
                                      .isChecked1,
                                  onChanged: (value) => context
                                      .read<InsertionUserInfoViewModel>()
                                      .clicked1stCheckBox(value),
                                  shape: const CircleBorder(),
                                  activeColor: Palette.primary,
                                  checkColor: Colors.white,
                                ),
                                Text('약관 전체 동의', style: Palette.h5),
                              ],
                            ),
                            const CustomDivider(height: 0),

                            // 개인정보 수집/제공 동의
                            Row(
                              children: [
                                Checkbox(
                                  value: context
                                      .watch<InsertionUserInfoViewModel>()
                                      .isChecked2,
                                  onChanged: (value) => context
                                      .read<InsertionUserInfoViewModel>()
                                      .clicked2ndCheckBox(value),
                                  shape: const CircleBorder(),
                                  activeColor: Palette.primary,
                                  checkColor: Colors.white,
                                ),
                                Text('(필수) 개인정보 수집/제공 동의', style: Palette.h5),
                                const Spacer(),
                                InkWell(
                                  onTap: () => showTermsPopup(context),
                                  child: Container(
                                    margin: EdgeInsets.only(right: 24.w),
                                    child: Icon(
                                      Icons.arrow_forward_ios,
                                      size: 20.sp,
                                    ),
                                  ),
                                )
                              ],
                            ),

                            // 제 3자 정보 제공 동의
                            Row(
                              children: [
                                Checkbox(
                                  value: context
                                      .watch<InsertionUserInfoViewModel>()
                                      .isChecked3,
                                  onChanged: (value) => context
                                      .read<InsertionUserInfoViewModel>()
                                      .clicked3rdCheckBox(value),
                                  shape: const CircleBorder(),
                                  activeColor: Palette.primary,
                                  checkColor: Colors.white,
                                ),
                                Text('(필수) 제 3자 정보 제공 동의', style: Palette.h5),
                                const Spacer(),
                                InkWell(
                                  onTap: () => showTermsPopup(context),
                                  child: Container(
                                    margin: EdgeInsets.only(right: 24.w),
                                    child: Icon(
                                      Icons.arrow_forward_ios,
                                      size: 20.sp,
                                    ),
                                  ),
                                )
                              ],
                            ),

                            // 알림 수신 동의
                            Row(
                              children: [
                                Checkbox(
                                  value: context
                                      .watch<InsertionUserInfoViewModel>()
                                      .isChecked4,
                                  onChanged: (value) => context
                                      .read<InsertionUserInfoViewModel>()
                                      .clicked4thCheckBox(value),
                                  shape: const CircleBorder(),
                                  activeColor: Palette.primary,
                                  checkColor: Colors.white,
                                ),
                                Text('(선택) 알림 수신 동의', style: Palette.h5),
                              ],
                            ),
                          ],
                        ),
                      ),
                      SizedBox(height: 64.h),

                      Container(
                        margin: EdgeInsets.only(bottom: 40.h),
                        child: MainButton(
                          width: double.infinity,
                          height: 96.h,
                          text: '다음',
                          onPressed: context
                                  .read<InsertionUserInfoViewModel>()
                                  .isAllChecked()
                              ? () => context
                                  .read<InsertionUserInfoViewModel>()
                                  .clickedNextButton(context)
                              : null,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            context.watch<InsertionUserInfoViewModel>().emailCheckLoading
                ? const Center(child: LoadingScreen())
                : Container(),
          ],
        ),
      ),
    );
  }
}

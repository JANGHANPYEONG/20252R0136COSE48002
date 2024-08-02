import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:flutter_svg/svg.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/loading_screen.dart';
import 'package:structure/components/main_button.dart';
import 'package:structure/components/main_input_field.dart';
import 'package:structure/config/palette.dart';
import 'package:structure/config/pallete.dart';
import 'package:structure/viewModel/sign_in/sign_in_view_model.dart';

class SignInScreen extends StatefulWidget {
  const SignInScreen({super.key});

  @override
  State<SignInScreen> createState() => _SignInScreenState();
}

class _SignInScreenState extends State<SignInScreen> {
  @override
  void initState() {
    super.initState();
    Future.delayed(Duration.zero, () {
      context.read<SignInViewModel>().autoLoginCheck(context);
    });
  }

  @override
  Widget build(BuildContext context) {
    SignInViewModel signInViewModel = context.watch<SignInViewModel>();

    return GestureDetector(
      onTap: () => FocusScope.of(context).unfocus(),
      child: Scaffold(
        body: Stack(
          children: [
            Center(
              child: SingleChildScrollView(
                child: Form(
                  key: signInViewModel.formKey,
                  child: Container(
                    margin: EdgeInsets.symmetric(horizontal: 40.w),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // 딥에이징 로고
                        Center(
                          child: Column(
                            children: [
                              SvgPicture.asset(
                                'assets/images/deepplant_logo.svg',
                                width: 240.w,
                              ),
                              SvgPicture.asset(
                                'assets/images/deepaging_logo.svg',
                                width: 380.w,
                              ),
                            ],
                          ),
                        ),
                        SizedBox(height: 96.h),

                        // 아이디 입력 필드
                        Text('이메일', style: Palette.h5SemiBoldSecondary),
                        SizedBox(height: 16.h),

                        MainInputField(
                          mode: 0,
                          width: double.infinity,
                          onChangeFunc: (value) =>
                              signInViewModel.userId = value,
                        ),
                        SizedBox(height: 16.h),

                        // 비밀번호 입력 필드
                        Text('비밀번호', style: Palette.h5SemiBoldSecondary),
                        SizedBox(height: 16.h),

                        MainInputField(
                          mode: 0,
                          width: double.infinity,
                          formKey: signInViewModel.formKey,
                          obscureText: true,
                          onChangeFunc: (value) =>
                              signInViewModel.userPw = value,
                        ),
                        SizedBox(height: 88.h),

                        // 로그인 버튼
                        MainButton(
                          mode: 0,
                          width: double.infinity,
                          height: 96.h,
                          text: '로그인',
                          onPressed: () async => await signInViewModel
                              .clickedSignInButton(context),
                        ),
                        SizedBox(height: 32.h),

                        // 자동로그인 체크박스
                        Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            SizedBox(
                              width: 32.w,
                              height: 32.h,
                              child: Checkbox(
                                value: signInViewModel.isAutoLogin,
                                onChanged: (value) =>
                                    signInViewModel.clickedAutoLogin(value!),
                                side: BorderSide(
                                  color: Colors.black,
                                  width: 1.sp,
                                ),
                                activeColor: Palette.primary,
                              ),
                            ),
                            SizedBox(width: 24.w),

                            Text('자동 로그인', style: Pallete.h5),
                            const Spacer(),

                            // 비밀번호 재설정.
                            TextButton(
                              onPressed: () =>
                                  signInViewModel.resetPassword(context),
                              child: Text(
                                '비밀번호 재설정',
                                style: Palette.h5.copyWith(
                                    decoration: TextDecoration.underline),
                              ),
                            ),

                            // 회원가입 텍스트버튼
                            TextButton(
                              onPressed: () => signInViewModel.signUp(context),
                              child: Text(
                                '회원가입',
                                style: Palette.h5.copyWith(
                                    decoration: TextDecoration.underline),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
            signInViewModel.isLoading
                ? const Center(child: LoadingScreen())
                : Container(),
          ],
        ),
      ),
    );
  }
}

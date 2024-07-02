import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:flutter_svg/svg.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/loading_screen.dart';
import 'package:structure/components/main_button.dart';
import 'package:structure/components/main_input_field.dart';
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
    return GestureDetector(
      onTap: () => FocusScope.of(context).unfocus(),
      child: Scaffold(
        backgroundColor: Colors.white,
        body: Stack(
          children: [
            Center(
              child: SingleChildScrollView(
                child: Form(
                  key: context.read<SignInViewModel>().formKey,
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      SvgPicture.asset(
                        'assets/images/deepplant_logo.svg',
                        width: 240.w,
                      ),
                      SvgPicture.asset(
                        'assets/images/deepaging_logo.svg',
                        width: 380.w,
                      ),

                      SizedBox(
                        height: 95.h,
                      ),
                      // 아이디 입력 필드
                      Container(
                          margin: EdgeInsets.only(left: 40.w, bottom: 10.h),
                          alignment: Alignment.centerLeft,
                          child: Text(
                            '이메일',
                            style: Palette.fieldTitle,
                          )),
                      MainInputField(
                        mode: 0,
                        width: 640.w,
                        onChangeFunc: (value) =>
                            context.read<SignInViewModel>().userId = value,
                      ),
                      SizedBox(
                        height: 35.h,
                      ),
                      // 비밀번호 입력 필드
                      Container(
                          margin: EdgeInsets.only(left: 40.w, bottom: 10.h),
                          alignment: Alignment.centerLeft,
                          child: Text(
                            '비밀번호',
                            style: Palette.fieldTitle,
                          )),
                      MainInputField(
                        mode: 0,
                        obscureText: true,
                        formKey: context.read<SignInViewModel>().formKey,
                        width: 640.w,
                        onChangeFunc: (value) =>
                            context.read<SignInViewModel>().userPw = value,
                      ),
                      SizedBox(
                        height: 90.h,
                      ),
                      // 로그인 버튼
                      MainButton(
                        mode: 0,
                        text: '로그인',
                        onPressed: () async => await context
                            .read<SignInViewModel>()
                            .clickedSignInButton(context),
                        width: 640.w,
                        height: 96.h,
                      ),
                      SizedBox(
                        height: 36.h,
                      ),
                      // 자동로그인 체크박스
                      SizedBox(
                        width: 640.w,
                        child: Row(
                          children: [
                            SizedBox(
                              width: 32.w,
                              height: 32.h,
                              child: Checkbox(
                                value: context
                                    .watch<SignInViewModel>()
                                    .isAutoLogin,
                                onChanged: (value) => context
                                    .read<SignInViewModel>()
                                    .clickedAutoLogin(value!),
                                side: BorderSide(
                                  color: Colors.black,
                                  width: 1.sp,
                                ),
                                activeColor: Palette.mainBtnAtvBg,
                              ),
                            ),
                            SizedBox(
                              width: 23.w,
                            ),
                            Text('자동 로그인', style: Palette.h5),
                            const Spacer(),
                            // 비밀번호 재설정.
                            TextButton(
                              onPressed: () {
                                FocusScope.of(context).unfocus();
                                context.go('/sign-in/password_reset');
                              },
                              child: Text(
                                '비밀번호 재설정 >',
                                style: Palette.h5.copyWith(
                                    color: Colors.black,
                                    decoration: TextDecoration.underline),
                              ),
                            ),
                            // 회원가입 텍스트버튼
                            TextButton(
                              onPressed: () {
                                FocusScope.of(context).unfocus();
                                context.go('/sign-in/sign-up');
                              },
                              child: Text(
                                '회원가입 >',
                                style: Palette.h5.copyWith(
                                    color: Colors.black,
                                    decoration: TextDecoration.underline),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            Center(
              child: // 데이터를 처리하는 동안 로딩 위젯 보여주기
                  context.watch<SignInViewModel>().isLoading
                      ? const LoadingScreen()
                      : Container(),
            ),
          ],
        ),
      ),
    );
  }
}

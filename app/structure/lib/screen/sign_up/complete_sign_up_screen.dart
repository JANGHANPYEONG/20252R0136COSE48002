import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:go_router/go_router.dart';
import 'package:structure/components/main_button.dart';
import 'package:structure/config/palette.dart';

class CompleteSignUpScreen extends StatelessWidget {
  const CompleteSignUpScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        margin: EdgeInsets.symmetric(horizontal: 40.w),
        child: Column(
          children: [
            Expanded(
              child: Stack(
                children: [
                  Center(
                    child: Transform.translate(
                      offset: Offset(0, 96.h),
                      child: Stack(
                        children: [
                          const Positioned(
                            left: 0,
                            bottom: 0,
                            child: Icon(
                              Icons.auto_awesome,
                              color: Palette.starYellow,
                            ),
                          ),
                          Icon(
                            Icons.check_circle,
                            size: 120.w,
                            color: Palette.primary,
                          ),
                          const Positioned(
                            right: 0,
                            child: Icon(
                              Icons.auto_awesome,
                              color: Palette.starYellow,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),

                  // 회원가입 완료 텍스트
                  Container(
                    margin: EdgeInsets.only(top: 188.h),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('회원가입이\n완료되었습니다 !', style: Palette.h2),
                        SizedBox(
                          height: 13.h,
                        ),
                        Text('이메일 인증을 완료해주세요.', style: Palette.h5Secondary),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            // 로그인 버튼
            Container(
              margin: EdgeInsets.only(bottom: 40.h),
              child: MainButton(
                width: double.infinity,
                height: 96.h,
                text: '로그인',
                onPressed: () => context.go('/sign-in'),
              ),
            )
          ],
        ),
      ),
    );
  }
}

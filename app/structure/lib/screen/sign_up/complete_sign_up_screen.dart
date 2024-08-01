import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:go_router/go_router.dart';
import 'package:structure/components/main_button.dart';
import 'package:structure/config/pallete.dart';

class CompleteSignUpScreen extends StatelessWidget {
  const CompleteSignUpScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Column(
        children: [
          Expanded(
            child: Stack(
              children: [
                Center(
                  child: Transform.translate(
                    offset: Offset(0, 96.h),
                    child: Stack(
                      children: [
                        Positioned(
                          left: 0.w,
                          bottom: 0,
                          child: const Icon(
                            Icons.auto_awesome,
                            color: Pallete.starIcon,
                          ),
                        ),
                        Icon(
                          Icons.check_circle,
                          size: 120.w,
                          color: Pallete.mainBtnAtvBg,
                        ),
                        const Positioned(
                          right: 0,
                          child: Icon(
                            Icons.auto_awesome,
                            color: Pallete.starIcon,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                Container(
                  margin: EdgeInsets.only(left: 46.w, top: 182.h),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('회원가입이\n완료되었습니다 !', style: Pallete.h2),
                      SizedBox(
                        height: 13.h,
                      ),
                      Text('이메일 인증을 완료해주세요.', style: Pallete.h5Grey),
                    ],
                  ),
                ),
              ],
            ),
          ),
          Container(
            margin: EdgeInsets.only(bottom: 40.h),
            child: MainButton(
              onPressed: () => context.go('/sign-in'),
              text: '로그인',
              width: 640.w,
              height: 96.h,
              mode: 1,
            ),
          )
        ],
      ),
    );
  }
}

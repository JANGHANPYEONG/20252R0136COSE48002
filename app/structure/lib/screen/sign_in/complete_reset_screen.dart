import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:go_router/go_router.dart';
import 'package:structure/components/main_button.dart';
import 'package:structure/config/palette.dart';

class CompleteResetScreen extends StatelessWidget {
  const CompleteResetScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
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
                        // 완료 아이콘
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

                // 변경 완료 텍스트
                Container(
                  margin: EdgeInsets.fromLTRB(40.w, 188.h, 40.w, 0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('비밀번호 변경 메일이\n전송되었습니다 !', style: Palette.h2),
                      SizedBox(height: 16.h),
                      Text('이메일을 확인해주세요.', style: Palette.h5Secondary),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // 확인 버튼
          Container(
            margin: EdgeInsets.fromLTRB(40.w, 0, 40.w, 40.h),
            child: MainButton(
              width: double.infinity,
              height: 96.h,
              text: '확인',
              onPressed: () => context.go('/sign-in'),
            ),
          )
        ],
      ),
    );
  }
}

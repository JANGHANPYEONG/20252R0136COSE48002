import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:go_router/go_router.dart';
import 'package:structure/components/custom_text_button.dart';
import 'package:structure/components/main_button.dart';
import 'package:structure/config/palette.dart';

class CreationManagementNumFailScreen extends StatefulWidget {
  const CreationManagementNumFailScreen({super.key});

  @override
  State<CreationManagementNumFailScreen> createState() =>
      _CreationManagementNumFailScreenState();
}

class _CreationManagementNumFailScreenState
    extends State<CreationManagementNumFailScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        margin: EdgeInsets.symmetric(horizontal: 40.w),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              margin: EdgeInsets.only(top: 188.h),
              child: Text('관리 번호 생성에\n실패했습니다.', style: Palette.h2),
            ),

            Expanded(
              child: Center(child: Image.asset('assets/images/print_fail.png')),
            ),

            // QR 버튼
            MainButton(
              width: double.infinity,
              height: 96.h,
              text: '다시 등록하기',
              onPressed: () => context.go('/home/registration'),
            ),
            SizedBox(height: 16.h),

            // 홈 이동 버튼
            Container(
              margin: EdgeInsets.only(bottom: 40.h),
              alignment: Alignment.center,
              child: CustomTextButton(
                title: '홈으로 이동하기',
                onPressed: () => context.go('/home'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

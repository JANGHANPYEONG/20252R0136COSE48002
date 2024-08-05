import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';
import 'package:structure/config/palette.dart';
import 'package:structure/config/pallete.dart';

class CreationManagementNumLoadingScreen extends StatelessWidget {
  const CreationManagementNumLoadingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 40.w),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            margin: EdgeInsets.only(top: 188.h),
            child: Text('관리 번호를\n생성 중 입니다', style: Pallete.h2),
          ),
          Expanded(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              mainAxisSize: MainAxisSize.min,
              children: [
                SpinKitThreeBounce(
                  color: Palette.primary,
                  size: 48.w,
                ),
                SizedBox(height: 88.h),
                Center(child: Image.asset('assets/images/print.png')),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

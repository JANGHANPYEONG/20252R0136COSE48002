import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';
import 'package:structure/config/pallete.dart';

class CreationManagementNumLoadingScreen extends StatelessWidget {
  const CreationManagementNumLoadingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Container(
        margin: EdgeInsets.only(left: 46.w, top: 182.h),
        child: Text('관리 번호를\n생성 중 입니다.', style: Palette.h2),
      ),
      SizedBox(height: 80.h),
      const SpinKitThreeBounce(
        color: Palette.mainBtnAtvBg,
        size: 50.0,
      ),
      SizedBox(height: 90.h),
      Center(child: Image.asset('assets/images/print.png')),
    ]);
  }
}

//
//
// 일반 데이터 승인 육류 테이블
//
//

import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:structure/config/palette.dart';

class CustomTableBar extends StatelessWidget {
  const CustomTableBar({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      height: 64.h,
      padding: EdgeInsets.symmetric(horizontal: 16.w),
      color: Palette.onPrimaryContainer,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          SizedBox(
            width: 240.w,
            child: Text('관리번호', style: Palette.h5),
          ),
          Text('날짜', style: Palette.h5),
          const Spacer(),
          SizedBox(
            width: 100.w,
            child: Text('상태', style: Palette.h5),
          ),
          SizedBox(width: 54.w)
        ],
      ),
    );
  }
}

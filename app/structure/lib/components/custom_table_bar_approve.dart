//
//
// 일반 데이터 승인 육류 테이블
//
//

import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:structure/config/pallete.dart';

class CustomTableBarApprove extends StatelessWidget {
  const CustomTableBarApprove({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 64.h,
      padding: EdgeInsets.symmetric(horizontal: 16.w),
      color: Colors.grey[50],
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          SizedBox(
            width: 240.w,
            child: Text('관리번호', style: Pallete.h5),
          ),
          Text('날짜', style: Pallete.h5),
          const Spacer(),
          SizedBox(
            width: 100.w,
            child: Text('상태', style: Pallete.h5),
          ),
          SizedBox(width: 54.w)
        ],
      ),
    );
  }
}

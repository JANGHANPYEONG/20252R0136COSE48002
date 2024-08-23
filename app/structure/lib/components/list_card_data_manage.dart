//
//
// ListCardDataManage 위젯.
// 데이터 관리 페이지 - 추가정보 입력 탭에서 사용되는 데이터 출력 위젯
// 해당 위젯은 'Researcher' 권한에서 사용된다.
//
// 파라미터로는
// 1. 데이터 정보를 누를 때 수행할 기능을 정의.
// 2. 인덱스 번호
// 3. 이력 번호.
//
//

import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:structure/config/palette.dart';

class ListCardDataManage extends StatelessWidget {
  final int idx;
  final String meatId;
  final VoidCallback? onTap;

  const ListCardDataManage({
    super.key,
    required this.idx,
    required this.meatId,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(20.r),
      child: Container(
        padding: EdgeInsets.all(16.w),
        height: 80.h,
        child: Row(
          children: [
            // idx
            SizedBox(
              width: 56.w,
              child: Text(idx.toString(), style: Palette.h5OnSecondary),
            ),

            // 관리번호
            Text(meatId, style: Palette.h5SemiBold, textAlign: TextAlign.left),
            const Spacer(),

            // 오른쪽 화살표
            Icon(
              Icons.arrow_forward_ios_outlined,
              size: 32.sp,
              color: Colors.grey,
            )
          ],
        ),
      ),
    );
  }
}

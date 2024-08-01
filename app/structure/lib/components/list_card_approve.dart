import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:structure/config/pallete.dart';

class ListCardApprove extends StatelessWidget {
  final VoidCallback? onTap;
  final int idx;
  final String meatId;
  final String dayTime;
  final String statusType;

  const ListCardApprove({
    super.key,
    required this.onTap,
    required this.idx,
    required this.meatId,
    required this.dayTime,
    required this.statusType,
  });

  @override
  Widget build(BuildContext context) {
    final Map<String, int> statusToInt = {'대기중': 0, '승인': 1, '반려': 2};
    final List<Color> colors = [
      Pallete.waitingCardBg,
      Pallete.confirmCardBg,
      Pallete.rejectCardBg,
    ];

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(20.r),
      child: Container(
        padding: EdgeInsets.all(8.w),
        height: 72.h,
        child: Row(
          children: [
            // 관리번호
            SizedBox(
              width: 240.w,
              child: Text(
                meatId,
                style: Pallete.h5,
              ),
            ),

            // 날짜
            Text(dayTime, style: Pallete.h5, textAlign: TextAlign.left),
            const Spacer(),

            // 상태
            Container(
              width: 100.w,
              height: 42.h,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(8.r),
                color: colors[statusToInt[statusType]!],
              ),
              child: Center(child: Text(statusType, style: Pallete.h5White)),
            ),

            SizedBox(width: 24.w),

            // 오른쪽 화살표
            Icon(
              Icons.arrow_forward_ios_outlined,
              size: 30.sp,
              color: Colors.grey,
            ),
            SizedBox(width: 8.w),
          ],
        ),
      ),
    );
  }
}

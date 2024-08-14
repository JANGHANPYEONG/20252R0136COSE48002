import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:structure/config/palette.dart';

class ListCard extends StatelessWidget {
  final VoidCallback? onTap;
  final String meatId;
  final String dayTime;
  final String statusType;
  final int? dDay;
  final int? updatedAt;

  const ListCard({
    super.key,
    required this.onTap,
    required this.meatId,
    required this.dayTime,
    required this.statusType,
    this.dDay,
    this.updatedAt,
  });

  @override
  Widget build(BuildContext context) {
    final Map<String, int> statusToInt = {'대기중': 0, '승인': 1, '반려': 2};
    final List<Color> colors = [
      Palette.onSecondary,
      Palette.primary,
      Palette.error,
    ];

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(20.r),
      child: Container(
        padding: EdgeInsets.all(16.w),
        height: 80.h,
        child: Row(
          children: [
            // 관리번호
            SizedBox(
              width: 240.w,
              child: Text(
                meatId,
                style: Palette.h5,
              ),
            ),

            // 날짜
            Text(dayTime, style: Palette.h5, textAlign: TextAlign.left),
            const Spacer(),

            // 상태
            Stack(
              clipBehavior: Clip.none,
              children: [
                Container(
                  width: 104.w,
                  height: 40.h,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(20.r),
                    color: colors[statusToInt[statusType]!],
                  ),
                  child: Center(
                    child: Text(
                      statusType,
                      style: Palette.h5.copyWith(color: Colors.white),
                    ),
                  ),
                ),
                if (dDay != null && statusType != '승인')
                  Positioned(
                    left: 68.w,
                    bottom: 28.h,
                    child: Container(
                      width: 48.w,
                      height: 24.h,
                      decoration: BoxDecoration(
                        color: Palette.starYellow,
                        borderRadius: BorderRadius.circular(20.r),
                      ),
                      child: Center(
                        child: statusType != '반려'
                            ? Text(
                                'D-$dDay',
                                style: Palette.h7,
                                textAlign: TextAlign.center,
                              )
                            : Text(
                                'D-$updatedAt',
                                style: Palette.h7,
                                textAlign: TextAlign.center,
                              ),
                      ),
                    ),
                  )
              ],
            ),
            SizedBox(width: 24.w),

            // 오른쪽 화살표
            Icon(
              Icons.arrow_forward_ios_outlined,
              size: 32.sp,
              color: Colors.grey,
            ),
          ],
        ),
      ),
    );
  }
}

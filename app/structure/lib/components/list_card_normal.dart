//
//
// ListCardNormal 위젯.
// 데이터 관리 페이지에서 데이터 목록에 사용되는 데이터 출력 위젯
// 해당 위젯은 'Normal' 권한에서 사용된다.
//
// 파라미터로는
// 1. 데이터 정보를 누를 때 수행할 기능을 정의.
// 2. 데이터의 순서를 정의. (거의 사용되지 않음.)
// 3. 이력 번호.
// 4. 생성 날짜.
// 5. 상태 타입. (대기중, 승인, 반려)
// 6. 수정 가능까지 남은 일자.
//
//

import 'package:structure/config/pallete.dart';
import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

class ListCardNormal extends StatelessWidget {
  final VoidCallback? onTap;
  final String num;
  final String dayTime;
  final String statusType;
  final int dDay;
  const ListCardNormal({
    super.key,
    required this.onTap,
    required this.num,
    required this.dayTime,
    required this.statusType,
    required this.dDay,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      child: Container(
        width: 640.w,
        height: 72.w,
        decoration: BoxDecoration(
          border: Border(
            bottom: BorderSide(color: Pallete.fieldBorder, width: 1.sp),
          ),
        ),
        child: Row(
          children: [
            SizedBox(
              width: 200.w,
              child: Text(
                num,
                style: Pallete.h5,
              ),
            ),
            // const Spacer(),
            SizedBox(
              width: 80.w,
            ),
            SizedBox(
              width: 150.w,
              child: Text(
                dayTime,
                style: Pallete.filterContent,
              ),
            ),
            const Spacer(),
            statusType != "승인"
                ? Stack(
                    children: [
                      Image.asset(
                        "assets/images/admin_able.png",
                        width: 40.h,
                        height: 40.h,
                      ),
                      Positioned(
                        left: 13.w,
                        child: Container(
                          width: 36.w,
                          height: 16.h,
                          decoration: BoxDecoration(
                            color: Pallete.starIcon,
                            borderRadius: BorderRadius.all(
                              Radius.circular(28.5.sp),
                            ),
                          ),
                          alignment: Alignment.center,
                          child: Text(
                            'D-$dDay',
                            style: TextStyle(fontSize: 13.sp),
                          ),
                        ),
                      )
                    ],
                  )
                : Image.asset(
                    "assets/images/admin_unable.png",
                    width: 55.h,
                    height: 55.h,
                  ),
            SizedBox(
              width: 30.w,
            ),
            Icon(
              Icons.arrow_forward_ios_outlined,
              size: 30.sp,
            )
          ],
        ),
      ),
    );
  }
}

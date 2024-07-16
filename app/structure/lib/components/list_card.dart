//
//
// ListCard 위젯.
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

class ListCard extends StatelessWidget {
  final VoidCallback? onTap;
  final int idx;
  final String num;
  final String dayTime;
  final String statusType;
  final int dDay;
  final String userName;
  const ListCard({
    super.key,
    required this.onTap,
    required this.idx,
    required this.num,
    required this.dayTime,
    required this.statusType,
    required this.dDay,
    required this.userName,
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
            bottom: BorderSide(color: Palette.fieldBorder, width: 1.sp),
          ),
        ),
        child: Row(
          children: [
            SizedBox(
              child: Text(
                num,
                style: Palette.h5,
              ),
            ),
            const Spacer(),
            SizedBox(
              child: Text(
                userName,
                style: Palette.filterContent,
              ),
            ),
            const Spacer(),
            statusType == "대기중"
                ? Stack(
                    children: [
                      Container(
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(10.sp),
                          color: Palette.waitingCardBg,
                        ),
                        width: 101.w,
                        height: 42.h,
                        child: Center(
                          child: Text(
                            statusType,
                            style: Palette.h5White,
                          ),
                        ),
                      ),
                      if (dDay != -1)
                        Positioned(
                          right: 0,
                          child: Container(
                            width: 36.w,
                            height: 16.h,
                            decoration: BoxDecoration(
                              color: Palette.starIcon,
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
                        ),
                    ],
                  )
                : Container(
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(10.sp),
                      color: statusType == "승인"
                          ? Palette.confirmCardBg
                          : Palette.rejectCardBg,
                    ),
                    width: 101.w,
                    height: 42.h,
                    child: Center(
                      child: Text(
                        statusType,
                        style: Palette.h5White,
                      ),
                    ),
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

class ListCardResearcherApprove extends StatelessWidget {
  final VoidCallback? onTap;
  final int idx;
  final String num;
  final String dayTime;
  final String statusType;
  final int? dDay;
  final String userId;

  const ListCardResearcherApprove({
    super.key,
    required this.onTap,
    required this.idx,
    required this.num,
    required this.dayTime,
    required this.statusType,
    required this.userId,
    this.dDay,
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
            bottom: BorderSide(color: Palette.fieldBorder, width: 1.sp),
          ),
        ),
        child: Row(
          children: [
            SizedBox(
              child: Text(
                num,
                style: Palette.h5,
              ),
            ),
            const Spacer(),
            SizedBox(
              child: Text(
                userId,
                style: Palette.filterContent,
              ),
            ),
            const Spacer(),
            statusType == "대기중"
                ? Stack(
                    children: [
                      Container(
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(10.sp),
                          color: Palette.waitingCardBg,
                        ),
                        width: 101.w,
                        height: 42.h,
                        child: Center(
                          child: Text(
                            statusType,
                            style: Palette.h5White,
                          ),
                        ),
                      ),
                      Positioned(
                        right: 0,
                        child: Container(
                          width: 36.w,
                          height: 16.h,
                          decoration: BoxDecoration(
                            color: Palette.starIcon,
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
                : Container(
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(10.sp),
                      color: statusType == "승인"
                          ? Palette.confirmCardBg
                          : Palette.rejectCardBg,
                    ),
                    width: 101.w,
                    height: 42.h,
                    child: Center(
                      child: Text(
                        statusType,
                        style: Palette.h5White,
                      ),
                    ),
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

//
//
// ListCardResearcher 위젯.
// 데이터 관리 페이지에서 데이터 목록에 사용되는 데이터 출력 위젯
// 해당 위젯은 'Researcher' 권한에서 사용된다.
//
// 파라미터로는
// 1. 데이터 정보를 누를 때 수행할 기능을 정의.
// 2. 데이터의 순서를 정의. (거의 사용되지 않음.)
// 3. 이력 번호.
// 4. 생성 날짜.
// 5. 생성자(유저)의 id(계정)
//
//

class ListCardResearcher extends StatelessWidget {
  final VoidCallback? onTap;
  final int idx;
  final String num;
  final String dayTime;
  final String userId;

  const ListCardResearcher({
    super.key,
    required this.onTap,
    required this.idx,
    required this.num,
    required this.dayTime,
    required this.userId,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(20.r),
      child: Container(
        padding: EdgeInsets.all(16.w),
        height: 72.h,
        child: Row(
          children: [
            // idx
            SizedBox(
              width: 60.w,
              child: Text(
                idx.toString(),
                style: Palette.filterContent,
              ),
            ),

            // 관리번호
            Text(
              num,
              style: Palette.meatNumStyle,
              textAlign: TextAlign.left,
            ),
            const Spacer(),

            // 오른쪽 화살표
            Icon(
              Icons.arrow_forward_ios_outlined,
              size: 30.sp,
              color: Colors.grey,
            )
          ],
        ),
      ),
    );
  }
}

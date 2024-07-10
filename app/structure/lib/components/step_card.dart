//
//
// StepCard 위젯.
// 데이터 관리 페이지에서 데이터를 참조할 때, 사용되는 육류 정보 페이지
// 해당 위젯은 'Researcher' 권한에서 사용된다.
//
// 파라미터로는
// 1. 육류 정보의 단계를 지정한다.
// 2. 정보 입력이 온전히 완료되었음을 나타낸다.
// 3. 이전 단계가 진행 되었음을 나타낸다.
// 4. 단계 표현에 들어갈 이미지의 경로를 지정한다.
//
//

import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:structure/config/pallete.dart';

class StepCard extends StatelessWidget {
  final String mainText;
  // 0 - 미진행, 1 - 완료, 2 - 미완료, 3 - 수정 가능, 4 - 수정 불가
  final int? status;
  final String imageUrl;
  const StepCard({
    super.key,
    required this.mainText,
    this.status,
    required this.imageUrl,
  });

  @override
  Widget build(BuildContext context) {
    final List<Color> statusColor = [
      Palette.notEditableBg,
      Palette.completeBg,
      Palette.notCompleteBg,
      Palette.editableBg,
      Palette.notEditableBg,
    ];
    final List<String> statusString = [
      '미진행',
      '완료',
      '미완료',
      '수정',
      '수정 불가',
    ];
    final List<TextStyle> statusTextStyle = [
      Palette.notEditableText,
      Palette.completeText,
      Palette.notCompleteText,
      Palette.editableText,
      Palette.notEditableText,
    ];

    return Container(
      padding: EdgeInsets.symmetric(horizontal: 5.w, vertical: 10.h),
      width: 588.w,
      height: 109.h,
      decoration: const BoxDecoration(
        border: null,
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // 이미지 지정
          Image.asset(imageUrl, width: 62.w, height: 62.h),
          SizedBox(width: 35.w),

          // 메인 텍스트
          Text(mainText, style: Palette.h4),
          const Spacer(),

          // status 상자 - null이면 표시하지 않음
          if (status != null)
            Container(
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(10.sp),
                color: statusColor[status!],
              ),
              width: 108.w,
              height: 48.h,
              child: Center(
                child: Text(
                  statusString[status!],
                  style: statusTextStyle[status!],
                ),
              ),
            ),
          SizedBox(width: 20.w),

          // 오른쪽 화살표
          Image.asset('assets/images/arrow-r.png', width: 33.w, height: 33.h),
        ],
      ),
    );
  }
}

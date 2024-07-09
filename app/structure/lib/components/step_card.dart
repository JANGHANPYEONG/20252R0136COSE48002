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
  final bool isCompleted;
  final bool isBefore;
  final String imageUrl;
  const StepCard({
    super.key,
    required this.mainText,
    required this.isCompleted,
    required this.isBefore,
    required this.imageUrl,
  });

  @override
  Widget build(BuildContext context) {
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
          Image.asset(
            imageUrl,
            width: 62.w,
            height: 62.h,
          ),
          SizedBox(
            width: 35.w,
          ),
          // 메인 텍스트
          Text(mainText, style: Palette.h4),
          const Spacer(),
          Container(
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(10.sp),
              // 이전 단계, 데이터 입력에 따라 색을 다르게 사용한다.
              color: isBefore
                  ? Palette.notEditableBg
                  : isCompleted
                      ? Palette.completeBg
                      : Palette.notCompleteBg,
            ),
            width: 108.w,
            height: 48.h,
            child: Center(
              child: Text(
                // 이전 단계, 데이터 입력에 따라 텍스트 스타일을 다르게 사용한다.
                isBefore
                    ? '미진행'
                    : isCompleted
                        ? '완료'
                        : '미완료',
                style: isBefore
                    ? Palette.notEditableText
                    : isCompleted
                        ? Palette.completeText
                        : Palette.notCompleteText,
              ),
            ),
          ),
          SizedBox(
            width: 20.w,
          ),
          Image.asset(
            'assets/images/arrow-r.png',
            width: 33.w,
            height: 33.h,
          ),
        ],
      ),
    );
  }
}

//
//
// StepCard2 위젯.
// 데이터 관리 페이지에서 데이터를 참조할 때, 사용되는 육류 정보 페이지
// 해당 위젯은 'Normal' 권한에서 사용된다.
//
// 파라미터로는
// 1. 육류 정보의 단계를 지정한다.
// 2. 데이터의 수정이 가능한 상태인지를 나타낸다.
// 3. 단계 표현에 들어갈 이미지의 경로를 지정한다.
//
//
class StepCard2 extends StatelessWidget {
  final String mainText;
  final bool isEditable;
  final String imageUrl;
  const StepCard2({
    super.key,
    required this.mainText,
    required this.isEditable,
    required this.imageUrl,
  });

  @override
  Widget build(BuildContext context) {
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
          Image.asset(
            imageUrl,
            width: 62.w,
            height: 62.h,
          ),
          SizedBox(
            width: 35.w,
          ),
          // 메인 텍스트
          Text(mainText, style: Palette.h4),
          const Spacer(),
          Container(
            // 데이터 수정이 가능한지에 따라 색을 다르게 한다.
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(10.sp),
              color: isEditable ? Palette.editableBg : Palette.notEditableBg,
            ),
            width: 108.w,
            height: 48.h,
            child: Center(
              // 데이터 수정이 가능한지에 따라 텍스트 스타일을 다르게 한다.
              child: Text(
                isEditable ? '수정' : '수정 불가',
                style:
                    isEditable ? Palette.editableText : Palette.notEditableText,
              ),
            ),
          ),
          SizedBox(
            width: 20.w,
          ),
          Image.asset(
            'assets/images/arrow-r.png',
            width: 33.w,
            height: 33.h,
          ),
        ],
      ),
    );
  }
}

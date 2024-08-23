//
//
// DeepAgingCard 위젯.
// 데이터 추가 입력 페이지에서, 딥에이징 데이터 카드 표현에 사용.
// 해당 위젯은 'Researcher' 권한에서 사용된다.
//
// 파라미터로는
// 1. 딥에이징 회차.
// 2. 딥에이징 처리 시간.
// 3. 도축 일자.
// 4. 데이터의 온전성 (모든 데이터 입력)
// 5. 마지막 회차인지 확인 (삭제 버튼을 추가하기 위함.)
// 6. 카드를 클릭할 때 수행할 기능 정의.
// 7. 삭제 버튼을 누를 때 수행할 기능 정의.
//
//
import 'package:structure/components/custom_dialog.dart';
import 'package:structure/config/palette.dart';
import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:structure/config/usefuls.dart';

class DeepAgingCard extends StatelessWidget {
  final bool isRaw;
  final String deepAgingNum;
  final String mainText;
  final String butcheryDate;
  final int completed;
  final VoidCallback onTap;
  final VoidCallback? delete;
  const DeepAgingCard({
    super.key,
    this.isRaw = false,
    required this.deepAgingNum,
    required this.mainText,
    required this.butcheryDate,
    required this.completed,
    required this.onTap,
    this.delete,
  });

  @override
  Widget build(BuildContext context) {
    final List<String> completedText = ['미완료', '진행중', '완료'];
    final List<Color> completedColor = [
      Palette.error,
      Palette.onError,
      Palette.primary
    ];

    return Stack(
      children: [
        SizedBox(
          height: 136.h,
          width: double.infinity,
          child: OutlinedButton(
            onPressed: onTap,
            style: OutlinedButton.styleFrom(
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(20.r),
              ),
              side: const BorderSide(color: Palette.onPrimaryContainer),
            ),
            child: Padding(
              padding: EdgeInsets.symmetric(vertical: 16.h),
              child: Row(
                children: [
                  SizedBox(
                    width: 344.w,
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            // 딥에이징 회차
                            if (!isRaw)
                              Container(
                                decoration: BoxDecoration(
                                  borderRadius: BorderRadius.circular(20.r),
                                  color: Palette.deepAgingNumBG,
                                ),
                                width: 80.w,
                                height: 32.h,
                                child: Center(
                                  child: Text(
                                    deepAgingNum,
                                    style: Palette.h5SemiBold.copyWith(
                                        color: Palette.deepAgingNumText),
                                  ),
                                ),
                              ),
                            if (!isRaw) SizedBox(width: 16.w),

                            // 도축/등록 날짜
                            Text(Usefuls.butcheryDateToDateShort(butcheryDate),
                                style: Palette.h5OnSecondary),
                          ],
                        ),
                        SizedBox(height: 16.h),

                        // Main text
                        Text(mainText, style: Palette.h3),
                      ],
                    ),
                  ),
                  VerticalDivider(thickness: 1, color: Colors.grey[300]),

                  // 추가정보 입력 완료 여부
                  SizedBox(
                    width: 160.w,
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('추가정보 입력', style: Palette.h5OnSecondary),
                        SizedBox(height: 16.h),

                        // 데이터 입력 확인
                        Text(
                          completedText[completed],
                          style: Palette.h4.copyWith(
                            color: completedColor[completed],
                          ),
                        ),
                      ],
                    ),
                  )
                ],
              ),
            ),
          ),
        ),

        // 삭제 버튼
        if (!isRaw)
          Positioned(
            top: -5.h,
            right: -10.w,
            child: IconButton(
              onPressed: () => showDeepAgingDeleteDialog(context, delete),
              icon: Icon(
                Icons.delete,
                size: 32.sp,
                color: Palette.onSecondary,
              ),
            ),
          )
      ],
    );
  }
}

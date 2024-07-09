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
import 'package:structure/config/pallete.dart';
import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

class DeepAgingCard extends StatelessWidget {
  final String deepAgingNum;
  final int minute;
  final String butcheryDate;
  final bool completed;
  final bool isLast;
  final VoidCallback onTap;
  final VoidCallback? delete;
  const DeepAgingCard({
    super.key,
    required this.deepAgingNum,
    required this.minute,
    required this.butcheryDate,
    required this.completed,
    required this.isLast,
    required this.onTap,
    this.delete,
  });

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        SizedBox(
          height: 133.h,
          child: OutlinedButton(
            onPressed: onTap,
            style: OutlinedButton.styleFrom(
              shape: RoundedRectangleBorder(
                borderRadius:
                    BorderRadius.circular(15), // Makes the border rectangular
              ),
              side: const BorderSide(
                color: Color(0xFFEAEAEA),
              ),
            ),
            child: Padding(
              padding: EdgeInsets.symmetric(vertical: 15.h),
              child: Row(
                children: [
                  SizedBox(
                    width: 340.w,
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Container(
                              decoration: BoxDecoration(
                                borderRadius: BorderRadius.circular(20.sp),
                                color: const Color.fromARGB(255, 232, 229, 255),
                              ),
                              width: 84.w,
                              height: 32.h,
                              child: Center(
                                child: Text(deepAgingNum),
                              ),
                            ),
                            SizedBox(
                              width: 10.w,
                            ),
                            Text(butcheryDate, style: Palette.h5Grey),
                          ],
                        ),
                        SizedBox(
                          height: 15.h,
                        ),
                        Text(
                          '$minute분',
                          style: TextStyle(
                              fontSize: 36.sp,
                              fontWeight: FontWeight.w700,
                              color: Colors.black),
                        ),
                      ],
                    ),
                  ),
                  VerticalDivider(
                    thickness: 1,
                    color: Colors.grey[300],
                  ),
                  SizedBox(
                    width: 160.w,
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('추가정보 입력', style: Palette.h5LightGrey),
                        SizedBox(
                          height: 15.h,
                        ),
                        Text(
                          completed ? '완료' : '미완료',
                          style: TextStyle(
                            fontSize: 28.sp,
                            fontWeight: FontWeight.w700,
                            color: completed
                                ? const Color.fromARGB(255, 56, 197, 95)
                                : const Color.fromARGB(255, 255, 73, 73),
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
        isLast == true
            ? Positioned(
                top: -5.h,
                right: -10.w,
                child: IconButton(
                  onPressed: delete,
                  icon: Icon(
                    Icons.delete,
                    size: 30.sp,
                    color: Palette.greyTextColor,
                  ),
                ),
              )
            : Container(),
      ],
    );
  }
}

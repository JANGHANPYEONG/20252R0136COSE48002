//
//
// FilterRow 컴포넌트 : Researcher
//
// 매개변수
// 1. 필터의 요소들이 들어감. (날짜, 정렬 방식, 육종 등)
// 2. 필터를 클릭할 때, 작업할 내용이 들어감.
// 3. 필터의 작용을 관리할 리스트 (어느 버튼이 눌린지를 체크)
//

import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:structure/config/pallete.dart';

class FilterRow extends StatelessWidget {
  const FilterRow({
    super.key,
    required this.filterList,
    required this.onTap,
    required this.status,
  });

  final List<String> filterList;
  final Function? onTap;
  final List<bool> status;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      keyboardDismissBehavior: ScrollViewKeyboardDismissBehavior.onDrag,
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: List.generate(
          filterList.length,
          growable: false,
          (index) => InkWell(
            onTap: onTap != null ? () => onTap!(index) : null,
            splashColor: Colors.transparent,
            highlightColor: Colors.transparent,
            child: Container(
              height: 48.h,
              margin: EdgeInsets.only(right: 12.w),
              alignment: Alignment.center,
              padding: EdgeInsets.symmetric(horizontal: 32.w),
              decoration: BoxDecoration(
                color: status[index] ? Colors.white : Pallete.fieldEmptyBg,
                borderRadius: BorderRadius.all(Radius.circular(50.r)),
                border: Border.all(
                  color:
                      status[index] ? Pallete.editableBg : Colors.transparent,
                ),
              ),
              child: Text(
                filterList[index],
                style: TextStyle(
                  color: status[index]
                      ? Pallete.editableBg
                      : Pallete.waitingCardBg,
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

//
//
// CustomTableCalendar 위젯.
// 데이터 관리 페이지에서 필터 기능에 사용된다.
//
// 파라미터로는
// 1, 2. 날짜를 정의하기 위해 사용되는 기본 변수이다. (일반적으로 수정이 권장되지는 않음.)
// 3. 위쪽에 위치하는 '월'을 선택할 시 작동되는 기능이다. (지금은 사용되지 않음.)
// 4. 날짜 변경을 위해 사용되는 함수이다.
//
//

import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:structure/config/pallete.dart';
import 'package:table_calendar/table_calendar.dart';

class CustomTableCalendar extends StatelessWidget {
  final DateTime focusedDay;
  final DateTime selectedDay;
  final Function(DateTime)? onHeaderTapped;
  final Function(DateTime, DateTime) onDaySelected;
  const CustomTableCalendar({
    super.key,
    required this.focusedDay,
    required this.selectedDay,
    this.onHeaderTapped,
    required this.onDaySelected,
  });

  @override
  Widget build(BuildContext context) {
    return TableCalendar(
      // 달력의 범위를 결정한다.
      firstDay: DateTime.utc(1970, 1, 1),
      lastDay: DateTime.utc(2032, 12, 31),
      focusedDay: focusedDay,
      rowHeight: 40,
      onHeaderTapped: onHeaderTapped,
      onDaySelected: onDaySelected,
      locale: 'ko-KR',

      // 날짜 변경을 위해 사용되는 고유 함수. (수정이 권장되지 않음.)
      selectedDayPredicate: (day) => isSameDay(selectedDay, day),
      headerStyle: HeaderStyle(
        formatButtonVisible: false,
        titleCentered: true,
        titleTextStyle: TextStyle(
          fontSize: 24.sp,
          fontWeight: FontWeight.bold,
        ),
        headerMargin: EdgeInsets.only(bottom: 36.h),
      ),
      calendarStyle: CalendarStyle(
        isTodayHighlighted: false,
        outsideDaysVisible: false,
        selectedDecoration: const BoxDecoration(
          color: Palette.checkSpeciesColor,
          shape: BoxShape.circle,
        ),
        selectedTextStyle: TextStyle(
          color: Colors.white,
          fontSize: 26.sp,
        ),
        defaultTextStyle: TextStyle(
          color: Colors.black,
          fontSize: 26.sp,
        ),
        todayTextStyle: TextStyle(
          color: Colors.black,
          fontSize: 26.sp,
        ),
      ),
    );
  }
}

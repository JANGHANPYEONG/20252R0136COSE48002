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
      firstDay: DateTime.utc(2023, 1, 1),
      lastDay: DateTime.utc(2032, 12, 31),
      focusedDay: focusedDay,
      rowHeight: 40.0,
      onHeaderTapped: onHeaderTapped,
      onDaySelected: onDaySelected,
      // 날짜 변경을 위해 사용되는 고유 함수. (수정이 권장되지 않음.)
      selectedDayPredicate: (day) => isSameDay(selectedDay, day),
      headerStyle: HeaderStyle(
        formatButtonVisible: false,
        titleCentered: true,
        titleTextStyle: TextStyle(
          fontSize: 25.sp,
          fontWeight: FontWeight.bold,
        ),
        headerMargin: const EdgeInsets.only(bottom: 25.0),
      ),
      calendarStyle: const CalendarStyle(
        isTodayHighlighted: false,
        outsideDaysVisible: false,
        selectedTextStyle: TextStyle(
          color: Colors.black,
          fontSize: 20.0,
          fontWeight: FontWeight.bold,
        ),
        defaultTextStyle: TextStyle(
          color: Colors.black,
          fontSize: 16.0,
        ),
        todayTextStyle: TextStyle(
          color: Colors.black,
          fontSize: 16.0,
        ),
      ),
    );
  }
}

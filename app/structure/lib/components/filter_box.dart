//
//
// FilterBox 컴포넌트 : Researcher
//
//

import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:structure/components/custom_divider.dart';
import 'package:structure/components/custom_table_calendar.dart';
import 'package:structure/components/date_container.dart';
import 'package:structure/components/filter_row.dart';
import 'package:structure/components/main_button.dart';
import 'package:structure/config/pallete.dart';

class FilterBox extends StatelessWidget {
  //필터 종류 0:normal, 1: 관리자 추가정보입력, 2 : 관리자 일반데이터 승인
  final int type;

  // 조회기간
  final List<String> dateList;
  final Function? onTapDate;
  final List<bool> dateStatus;

  // 날짜
  final String firstDayText;
  final int indexDay;
  final dynamic Function()? firstDayOnTapTable;
  final String lastDayText;
  final dynamic Function()? lastDayOnTapTable;

  // 달력
  final bool isOpenTable;
  final DateTime focused;
  final dynamic Function(DateTime, DateTime) onDaySelected;

  // 데이터
  final List<String> dataList;
  final Function? onTapData;
  final List<bool> dataStatus;

  // 육종
  final List<String> speciesList;
  final Function? onTapSpecies;
  final List<bool> speciesStatus;

  // 조회 버튼
  final bool checkedFilter;
  final Function()? onPressedFilterSave;

  //상태 (대기중 : 0, 승인 : 2, 반려 : 1)
  final List<String>? statusList;
  final Function? onTapstatus;
  final List<bool>? statusStatus;

  const FilterBox({
    super.key,
    required this.type,
    required this.dateList,
    this.onTapDate,
    required this.dateStatus,
    required this.firstDayText,
    required this.indexDay,
    this.firstDayOnTapTable,
    required this.lastDayText,
    this.lastDayOnTapTable,
    required this.isOpenTable,
    required this.focused,
    required this.onDaySelected,
    required this.dataList,
    this.onTapData,
    required this.dataStatus,
    required this.speciesList,
    required this.onTapSpecies,
    required this.speciesStatus,
    this.statusList,
    this.onTapstatus,
    this.statusStatus,
    required this.checkedFilter,
    this.onPressedFilterSave,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 40.w),
      child: Column(
        children: [
          const CustomDivider(height: 16),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              // 조회 기간
              Text('조회 기간', style: Palette.fieldTitle),
              SizedBox(height: 16.h),

              // 조회기간 filterRow
              // FilterRow 컴포넌트를 이용하여 Filter list 표현
              FilterRow(
                filterList: dateList,
                onTap: onTapDate,
                status: dateStatus,
              ),

              // 직접입력일때만 height 생성
              dateStatus[3] ? SizedBox(height: 16.h) : Container(),

              // 날짜 컨테이너
              dateStatus[3]
                  ? Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        // 날짜를 '직접설정'으로 지정할 때, 사용되는 날짜 선택 기능
                        // 시작 날짜
                        DateContainer(
                          dateString: firstDayText,
                          dateStatus: dateStatus[3],
                          showDecoration: indexDay == 0,
                          onTap:
                              dateStatus[3] ? () => firstDayOnTapTable : null,
                        ),
                        SizedBox(width: 16.w),
                        const Text('-'),
                        SizedBox(width: 16.w),

                        // 날짜를 '직접설정'으로 지정할 때, 사용되는 날짜 선택 기능
                        // 끝 날짜
                        DateContainer(
                          dateString: lastDayText,
                          dateStatus: dateStatus[3],
                          showDecoration: indexDay == 1,
                          onTap: dateStatus[3] ? () => lastDayOnTapTable : null,
                        ),
                      ],
                    )
                  : Container(),

              // 달력
              // '직접설정'이 선택되었을 때, 표현되는 'CustomTableCalendar' 위젯 (날짜 선택 달력 위젯)
              isOpenTable
                  ? CustomTableCalendar(
                      focusedDay: focused,
                      selectedDay: focused,
                      onDaySelected: onDaySelected,
                    )
                  : Container(),
              SizedBox(height: 24.h),

              // 데이터
              Text('데이터', style: Palette.fieldTitle),
              SizedBox(height: 16.h),

              // 데이터 filterrow
              // FilterRow 컴포넌트를 이용하여 Filter list 표현
              FilterRow(
                filterList: dataList,
                onTap: onTapData,
                status: dataStatus,
              ),
              SizedBox(height: 24.h),

              // 육종
              Text('육종', style: Palette.fieldTitle),
              SizedBox(height: 16.h),

              // 육종 filterRow
              FilterRow(
                filterList: speciesList,
                onTap: onTapSpecies,
                status: speciesStatus,
              ),
              // type == 2 ? SizedBox(height: 24.h) : const Text(''),
              // type == 2
              //     ?
              //     // 상태
              //     Text('상태', style: Palette.fieldTitle)
              //     : const Text(''),
              // SizedBox(height: 16.h),
              // type == 2
              //     ? FilterRow(
              //         filterList: statusList!,
              //         onTap: onTapstatus,
              //         status: statusStatus!,
              //       )
              //     : const Text(''),
              // type == 2 ? SizedBox(height: 32.h) : const Text(''),
              Column(
                children: [
                  if (type == 2) SizedBox(height: 24.h),
                  if (type == 2) Text('상태', style: Palette.fieldTitle),
                  SizedBox(height: 16.h),
                  if (type == 2)
                    FilterRow(
                      filterList: statusList!,
                      onTap: onTapstatus,
                      status: statusStatus!,
                    ),
                  if (type == 2) SizedBox(height: 32.h),
                ],
              ),

              // 조회 버튼
              MainButton(
                text: '조회',
                width: 640.w,
                height: 72.h,
                mode: 1,
                onPressed: checkedFilter ? onPressedFilterSave : null,
              ),
            ],
          ),
          const CustomDivider(height: 16),
        ],
      ),
    );
  }
}

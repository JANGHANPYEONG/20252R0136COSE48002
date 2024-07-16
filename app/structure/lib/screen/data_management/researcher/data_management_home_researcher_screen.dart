//
//
// 추가정보 입력 페이지(View) : Researcher
//
//

import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_table_calendar.dart';
import 'package:structure/components/date_container.dart';
import 'package:structure/components/list_card.dart';
import 'package:structure/components/loading_screen.dart';
import 'package:structure/components/main_button.dart';
import 'package:structure/components/main_text_field.dart';
import 'package:structure/config/pallete.dart';
import 'package:structure/viewModel/data_management/researcher/data_management_researcher_view_model.dart';

class DataManagementHomeResearcherScreen extends StatefulWidget {
  const DataManagementHomeResearcherScreen({super.key});

  @override
  State<DataManagementHomeResearcherScreen> createState() =>
      _DataManagementHomeResearcherScreenState();
}

class _DataManagementHomeResearcherScreenState
    extends State<DataManagementHomeResearcherScreen> {
  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => FocusScope.of(context).unfocus(),
      child: Scaffold(
        backgroundColor: Colors.white,
        body: Stack(
          children: [
            SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.center,
                mainAxisSize: MainAxisSize.min,
                children: [
                  SizedBox(height: 20.h),

                  // 필터 버튼
                  Container(
                    margin: EdgeInsets.symmetric(horizontal: 40.w),
                    alignment: Alignment.centerRight,
                    child: InkWell(
                      onTap: () => context
                          .read<DataManagementHomeResearcherViewModel>()
                          .clickedFilter(context),
                      borderRadius: BorderRadius.circular(20.r),
                      child: Container(
                        padding: EdgeInsets.all(8.w),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            // 선택된 필터
                            Text(
                              context
                                  .watch<
                                      DataManagementHomeResearcherViewModel>()
                                  .filterdResult,
                              style: Palette.h4,
                            ),

                            // 화살표
                            context
                                    .watch<
                                        DataManagementHomeResearcherViewModel>()
                                    .isOpnedFilter
                                ? const Icon(Icons.arrow_drop_up_outlined)
                                : const Icon(Icons.arrow_drop_down),
                          ],
                        ),
                      ),
                    ),
                  ),

                  // 필터 area
                  context
                          .watch<DataManagementHomeResearcherViewModel>()
                          .isOpnedFilter
                      ? const ResercherFilterBox()
                      : SizedBox(height: 12.h),

                  // 관리번호 입력 textfield
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      // 'MainTextField' 컴포넌트를 이용하여 관리 번호 검색 기능을 정의한다.
                      MainTextField(
                        validateFunc: null,
                        onSaveFunc: null,
                        controller: context
                            .read<DataManagementHomeResearcherViewModel>()
                            .controller,
                        focusNode: context
                            .read<DataManagementHomeResearcherViewModel>()
                            .focusNode,
                        onChangeFunc: (value) => context
                            .read<DataManagementHomeResearcherViewModel>()
                            .onChanged(value),
                        mainText: '관리번호 입력',
                        hideFloatingLabel: true,
                        width: 560.w,
                        height: 72.h,
                        canAlert: true,
                        prefixIcon: const Icon(
                          Icons.search,
                          color: Palette.meatRegiCardBg,
                        ),
                        suffixIcon: context
                                .watch<DataManagementHomeResearcherViewModel>()
                                .focusNode
                                .hasFocus
                            ? IconButton(
                                onPressed: () {
                                  context
                                      .read<
                                          DataManagementHomeResearcherViewModel>()
                                      .textClear(context);
                                },
                                icon: const Icon(
                                  Icons.cancel,
                                  color: Palette.meatRegiCardBg,
                                ),
                              )
                            : null,
                      ),
                      IconButton(
                        // QR 코드 확인 기능을 정의한다.
                        iconSize: 48.w,
                        onPressed: () async => context
                            .read<DataManagementHomeResearcherViewModel>()
                            .clickedQr(context),
                        icon: const Icon(
                          Icons.qr_code_scanner_rounded,
                          color: Palette.meatRegiBtnBg,
                        ),
                      ),
                    ],
                  ),
                  SizedBox(height: 40.h),

                  // 육류 리스트
                  Container(
                    margin: EdgeInsets.symmetric(horizontal: 40.w),
                    height: 800.h,
                    child: Consumer<DataManagementHomeResearcherViewModel>(
                      // ListView 위젯을 활용하여, ListCard 출력 : 데이터 목록 표현
                      builder: (context, viewModel, child) =>
                          ListView.separated(
                        itemCount: viewModel.selectedList.length,
                        itemBuilder: (context, index) => ListCardResearcher(
                          onTap: () async =>
                              await viewModel.onTap(index, context),
                          idx: index + 1,
                          num: viewModel.selectedList[index]["id"]!,
                          dayTime: viewModel.selectedList[index]["dayTime"]!,
                          userId: viewModel.selectedList[index]['userId']!,
                        ),
                        keyboardDismissBehavior:
                            ScrollViewKeyboardDismissBehavior.onDrag,
                        separatorBuilder: (BuildContext context, int index) =>
                            const Divider(height: 5),
                      ),
                    ),
                  ),
                  SizedBox(height: 50.h),
                ],
              ),
            ),
            context.watch<DataManagementHomeResearcherViewModel>().isLoading
                ? const Center(child: LoadingScreen())
                : Container(),
          ],
        ),
      ),
    );
  }
}

//
//
// FilterBox 컴포넌트 : Researcher
//
//

class ResercherFilterBox extends StatelessWidget {
  const ResercherFilterBox({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 40.w),
      child: Column(
        children: [
          const Divider(height: 5),
          SizedBox(height: 16.h),

          // 조회 기간
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('조회 기간', style: Palette.fieldTitle),
              SizedBox(height: 16.h),
              // FilterRow 컴포넌트를 이용하여 Filter list 표현
              FilterRow(
                filterList: context
                    .watch<DataManagementHomeResearcherViewModel>()
                    .dateList,
                onTap: (index) => context
                    .read<DataManagementHomeResearcherViewModel>()
                    .onTapDate(index),
                status: context
                    .watch<DataManagementHomeResearcherViewModel>()
                    .dateStatus,
              ),
              SizedBox(height: 30.h),

              // 날짜 컨테이너
              context
                      .watch<DataManagementHomeResearcherViewModel>()
                      .dateStatus[3]
                  ? Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        // 날짜를 '직접설정'으로 지정할 때, 사용되는 날짜 선택 기능
                        // 시작 날짜
                        Consumer<DataManagementHomeResearcherViewModel>(
                          builder: (context, viewModel, child) => DateContainer(
                            dateString: viewModel.firstDayText,
                            dateStatus: viewModel.dateStatus[3],
                            showDecoration: viewModel.firstDayText != '' ||
                                viewModel.indexDay == 0,
                            onTap: (viewModel.dateStatus[3])
                                ? () => viewModel.onTapTable(0)
                                : null,
                          ),
                        ),
                        SizedBox(width: 20.w),
                        const Text('-'),
                        SizedBox(width: 20.w),
                        // 날짜를 '직접설정'으로 지정할 때, 사용되는 날짜 선택 기능
                        // 끝 날짜
                        Consumer<DataManagementHomeResearcherViewModel>(
                          builder: (context, viewModel, child) => DateContainer(
                            dateString: viewModel.lastDayText,
                            dateStatus: viewModel.dateStatus[3],
                            showDecoration: viewModel.lastDayText != '' ||
                                viewModel.indexDay == 1,
                            onTap: (viewModel.dateStatus[3])
                                ? () => viewModel.onTapTable(1)
                                : null,
                          ),
                        ),
                      ],
                    )
                  : Container(),
              SizedBox(height: 30.h),

              // 달력
              // '직접설정'이 선택되었을 때, 표현되는 'CustomTableCalendar' 위젯 (날짜 선택 달력 위젯)
              context.watch<DataManagementHomeResearcherViewModel>().isOpenTable
                  ? SizedBox(
                      child: Consumer<DataManagementHomeResearcherViewModel>(
                        builder: (context, viewModel, child) =>
                            CustomTableCalendar(
                          focusedDay: viewModel.focused,
                          selectedDay: viewModel.focused,
                          onDaySelected: (selectedDay, focusedDay) =>
                              viewModel.onDaySelected(selectedDay, focusedDay),
                        ),
                      ),
                    )
                  : Container(),
              SizedBox(height: 24.w),

              // 작성자
              Text('작성자', style: Palette.fieldTitle),
              SizedBox(
                height: 15.w,
              ),
              Column(
                children: [
                  SizedBox(
                    width: 15.w,
                  ),
                  // FilterRow 컴포넌트를 이용하여 Filter list 표현
                  FilterRow(
                      filterList: context
                          .watch<DataManagementHomeResearcherViewModel>()
                          .dataList,
                      onTap: (index) => context
                          .read<DataManagementHomeResearcherViewModel>()
                          .onTapData(index),
                      status: context
                          .watch<DataManagementHomeResearcherViewModel>()
                          .dataStatus),
                ],
              ),
              SizedBox(
                height: 15.w,
              ),
              Row(
                children: [
                  Text(
                    '육종',
                    style: Palette.fieldTitle,
                  ),
                ],
              ),
              SizedBox(
                height: 15.w,
              ),
              Row(
                children: [
                  SizedBox(
                    width: 15.w,
                  ),
                  // FilterRow 컴포넌트를 이용하여 Filter list 표현
                  FilterRow(
                      filterList: context
                          .watch<DataManagementHomeResearcherViewModel>()
                          .speciesList,
                      onTap: (index) => context
                          .read<DataManagementHomeResearcherViewModel>()
                          .onTapSpecies(index),
                      status: context
                          .watch<DataManagementHomeResearcherViewModel>()
                          .speciesStatus),
                ],
              ),
              SizedBox(
                height: 30.w,
              ),
              // 조회 버튼
              MainButton(
                text: '조회',
                width: 640.w,
                height: 70.h,
                mode: 1,
                onPressed: context
                        .read<DataManagementHomeResearcherViewModel>()
                        .checkedFilter()
                    ? () => context
                        .read<DataManagementHomeResearcherViewModel>()
                        .onPressedFilterSave()
                    : null,
              ),
            ],
          ),
          const Divider(),
        ],
      ),
    );
  }
}

//
//
// FilterRow 컴포넌트 : Researcher
//
// 매개변수
// 1. 필터의 요소들이 들어감. (날짜, 정렬 방식, 육종 등)
// 2. 필터를 클릭할 때, 작업할 내용이 들어감.
// 3. 필터의 작용을 관리할 리스트 (어느 버튼이 눌린지를 체크)
//

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
      child: Row(
        children: List.generate(
          filterList.length,
          (index) => InkWell(
            onTap: onTap != null ? () => onTap!(index) : null,
            splashColor: Colors.transparent,
            highlightColor: Colors.transparent,
            child: Container(
              height: 48.h,
              margin: EdgeInsets.only(right: 10.w),
              alignment: Alignment.center,
              padding: EdgeInsets.symmetric(horizontal: 30.w),
              decoration: BoxDecoration(
                  color: status[index] ? Colors.white : Palette.fieldEmptyBg,
                  borderRadius: BorderRadius.all(
                    Radius.circular(50.sp),
                  ),
                  border: Border.all(
                    color:
                        status[index] ? Palette.editableBg : Colors.transparent,
                  )),
              child: Text(
                filterList[index],
                style: TextStyle(
                  color: status[index]
                      ? Palette.editableBg
                      : Palette.waitingCardBg,
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

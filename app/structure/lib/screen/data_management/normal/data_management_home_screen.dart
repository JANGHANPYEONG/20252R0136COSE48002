//
//
// 데이터 관리 페이지(View) : Normal
//
//

import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/custom_table_bar.dart';
import 'package:structure/components/custom_table_calendar.dart';
import 'package:structure/components/filter_box.dart';
import 'package:structure/components/list_card_normal.dart';
import 'package:structure/components/loading_screen.dart';
import 'package:structure/components/main_button.dart';
import 'package:structure/components/main_text_field.dart';
import 'package:structure/config/pallete.dart';
import 'package:structure/config/userfuls.dart';
import 'package:structure/viewModel/data_management/normal/data_management_view_model.dart';

class DataManagementHomeScreen extends StatefulWidget {
  const DataManagementHomeScreen({super.key});

  @override
  State<DataManagementHomeScreen> createState() =>
      _DataManagementHomeScreenState();
}

class _DataManagementHomeScreenState extends State<DataManagementHomeScreen> {
  @override
  Widget build(BuildContext context) {
    DataManagementHomeViewModel dataManagementHomeViewModel =
        context.watch<DataManagementHomeViewModel>();

    return GestureDetector(
      onTap: () => FocusScope.of(context).unfocus(),
      child: Scaffold(
        backgroundColor: Colors.white,
        appBar: const CustomAppBar(
          title: '데이터 관리',
          backButton: true,
          closeButton: false,
        ),
        body: SingleChildScrollView(
          child: SizedBox(
            height: dataManagementHomeViewModel.isOpenTable
                ? MediaQuery.of(context).size.height + 120.h
                : MediaQuery.of(context).size.height - 120.h,
            child: Stack(
              children: [
                Column(
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        // 필터 버튼에 대한 기능을 정의한다.
                        InkWell(
                          // 필터 버튼을 누르면 'clickedFilter'함수를 참조한다.
                          onTap: () =>
                              dataManagementHomeViewModel.clickedFilter(),
                          child: Container(
                            alignment: Alignment.center,
                            child: Row(
                              children: [
                                Text(
                                  dataManagementHomeViewModel.filterdResult,
                                  style: Palette.h4,
                                ),
                                dataManagementHomeViewModel.isOpnedFilter
                                    ? const Icon(Icons.arrow_drop_up_outlined)
                                    : const Icon(Icons.arrow_drop_down),
                              ],
                            ),
                          ),
                        ),
                        SizedBox(width: 30.w),
                      ],
                    ),

                    // 'isOpendFilter'변수를 참조하여 filter를 표출한다.
                    dataManagementHomeViewModel.isOpnedFilter
                        ? FilterBox(
                            type: 0,
                            dateList: dataManagementHomeViewModel.dateList,
                            onTapDate: (index) =>
                                dataManagementHomeViewModel.onTapDate(index),
                            dateStatus: dataManagementHomeViewModel.dateStatus,
                            firstDayText:
                                dataManagementHomeViewModel.firstDayText,
                            indexDay: dataManagementHomeViewModel.indexDay,
                            firstDayOnTapTable: () =>
                                dataManagementHomeViewModel.onTapTable(0),
                            lastDayText:
                                dataManagementHomeViewModel.lastDayText,
                            lastDayOnTapTable: () =>
                                dataManagementHomeViewModel.onTapTable(1),
                            isOpenTable:
                                dataManagementHomeViewModel.isOpenTable,
                            focused: dataManagementHomeViewModel.focused,
                            onDaySelected: (selectedDay, focusedDay) =>
                                dataManagementHomeViewModel.onDaySelected(
                                    selectedDay, focusedDay),
                            // dataList: dataManagementHomeViewModel.dataList,
                            // onTapData: (index) =>
                            //     dataManagementHomeViewModel.onTapData(index),
                            // dataStatus: dataManagementHomeViewModel.dataStatus,
                            // speciesList: dataManagementHomeViewModel.speciesList,
                            // onTapSpecies: (index) =>
                            //     dataManagementHomeViewModel.onTapSpecies(index),
                            // speciesStatus: dataManagementHomeViewModel.speciesStatus,
                            checkedFilter:
                                dataManagementHomeViewModel.checkedFilter(),
                            onPressedFilterSave: () =>
                                dataManagementHomeViewModel
                                    .onPressedFilterSave(),
                            statusList: dataManagementHomeViewModel.statusList,
                            onTapstatus: (index) =>
                                dataManagementHomeViewModel.onTapStatus(index),
                            statusStatus:
                                dataManagementHomeViewModel.statusStatus,
                            sortList: dataManagementHomeViewModel.sortList,
                            onTapSort: (index) =>
                                dataManagementHomeViewModel.onTapSort(index),
                            sortStatus: dataManagementHomeViewModel.sortStatus)
                        // const NormalFilterBox()
                        : SizedBox(height: 10.h),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        // 'MainTextField' 컴포넌트를 이용하여 관리 번호 검색 기능을 정의한다.
                        MainTextField(
                          validateFunc: null,
                          onSaveFunc: null,
                          controller: dataManagementHomeViewModel.controller,
                          onChangeFunc: (value) =>
                              dataManagementHomeViewModel.onChanged(value),
                          focusNode: dataManagementHomeViewModel.focusNode,
                          mainText: '관리번호 입력',
                          width: 590.w,
                          height: 72.h,
                          canAlert: false,
                          prefixIcon: const Icon(Icons.search),
                          suffixIcon:
                              dataManagementHomeViewModel.focusNode.hasFocus
                                  ? IconButton(
                                      onPressed: () {
                                        dataManagementHomeViewModel
                                            .textClear(context);
                                      },
                                      icon: const Icon(
                                        Icons.cancel_outlined,
                                        color: Colors.black,
                                      ),
                                    )
                                  : null,
                        ),
                        IconButton(
                          // QR 코드 확인 기능을 정의한다.
                          iconSize: 48.w,
                          onPressed: () async =>
                              dataManagementHomeViewModel.clickedQr(context),
                          icon: const Icon(Icons.qr_code_scanner_rounded),
                        ),
                      ],
                    ),
                    Container(
                      margin: EdgeInsets.symmetric(vertical: 10.h),
                      // 'CustomTableBar' 컴포넌트를 통해 table label 지정.
                      child: const CustomTableNormalBar(
                        isNormal: true,
                      ),
                    ),
                    Expanded(
                      child: SizedBox(
                        width: 640.w,
                        child: Scrollbar(
                          thumbVisibility: true,
                          child: ListView.builder(
                            itemCount:
                                dataManagementHomeViewModel.selectedList.length,
                            itemBuilder: (context, index) => ListCardNormal(
                              onTap: () async =>
                                  await dataManagementHomeViewModel.onTap(
                                      index, context),
                              num: dataManagementHomeViewModel
                                  .selectedList[index]["meatId"]!,
                              dayTime: dataManagementHomeViewModel
                                  .selectedList[index]["createdAt"]!,
                              statusType: dataManagementHomeViewModel
                                  .selectedList[index]["statusType"]!,
                              dDay: 3 -
                                  Usefuls.calculateDateDifference(
                                    Usefuls.dateShortToDateLong(
                                        dataManagementHomeViewModel
                                            .selectedList[index]["createdAt"]!),
                                  ),
                            ),
                          ),
                        ),
                      ),
                    ),
                    SizedBox(height: 50.h),
                  ],
                ),
                dataManagementHomeViewModel.isLoading
                    ? const Center(child: LoadingScreen())
                    : Container(),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

//
//
// FilterBox 컴포넌트 : Normal
//
//

class NormalFilterBox extends StatelessWidget {
  const NormalFilterBox({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 30.w),
      child: Column(
        children: [
          const Divider(),
          SizedBox(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                Row(
                  children: [
                    Text(
                      '조회 기간',
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
                            .watch<DataManagementHomeViewModel>()
                            .dateList,
                        onTap: (index) => context
                            .read<DataManagementHomeViewModel>()
                            .onTapDate(index),
                        status: context
                            .watch<DataManagementHomeViewModel>()
                            .dateStatus),
                  ],
                ),
                SizedBox(
                  height: 15.w,
                ),
                context.watch<DataManagementHomeViewModel>().dateStatus[3]
                    ? Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          // 날짜를 '직접설정'으로 지정할 때, 사용되는 날짜 선택 기능
                          Consumer<DataManagementHomeViewModel>(
                            builder: (context, viewModel, child) => InkWell(
                              onTap: (viewModel.dateStatus[3])
                                  ? () => viewModel.onTapTable(0)
                                  : null,
                              child: Container(
                                width: 290.w,
                                height: 64.h,
                                decoration: BoxDecoration(
                                  color: viewModel.dateStatus[3]
                                      ? Palette.fieldEmptyBg
                                      : Palette.dataMngCardBg,
                                  borderRadius: BorderRadius.circular(20.w),
                                ),
                                alignment: Alignment.centerLeft,
                                padding: const EdgeInsets.only(left: 10.0),
                                child: Text(
                                  viewModel.firstDayText,
                                  style: viewModel.dateStatus[3]
                                      ? Palette.h5
                                      : Palette.h5LightGrey,
                                ),
                              ),
                            ),
                          ),
                          SizedBox(
                            width: 20.w,
                          ),
                          const Text('-'),
                          SizedBox(
                            width: 20.w,
                          ),
                          // 날짜를 '직접설정'으로 지정할 때, 사용되는 날짜 선택 기능
                          Consumer<DataManagementHomeViewModel>(
                            builder: (context, viewModel, child) => InkWell(
                              onTap: (viewModel.dateStatus[3])
                                  ? () => viewModel.onTapTable(1)
                                  : null,
                              // onTap :() => {},
                              child: Container(
                                width: 290.w,
                                height: 64.h,
                                decoration: BoxDecoration(
                                  color: viewModel.dateStatus[3]
                                      ? Palette.fieldEmptyBg
                                      : Palette.dataMngCardBg,
                                  borderRadius: BorderRadius.circular(20.w),
                                ),
                                alignment: Alignment.centerLeft,
                                padding: const EdgeInsets.only(left: 10.0),
                                child: Text(
                                  viewModel.lastDayText,
                                  style: Palette.h5,
                                ),
                              ),
                            ),
                          ),
                        ],
                      )
                    : Container(),
                SizedBox(
                  height: 15.w,
                ),
                // '직접설정'이 선택되었을 때, 표현되는 'CustomTableCalendar' 위젯 (날짜 선택 달력 위젯)
                context.watch<DataManagementHomeViewModel>().isOpenTable
                    ? SizedBox(
                        child: Consumer<DataManagementHomeViewModel>(
                          builder: (context, viewModel, child) =>
                              CustomTableCalendar(
                                  focusedDay: viewModel.focused,
                                  selectedDay: viewModel.focused,
                                  onDaySelected: (selectedDay, focusedDay) =>
                                      viewModel.onDaySelected(
                                          selectedDay, focusedDay)),
                        ),
                      )
                    : const SizedBox(),
                SizedBox(
                  height: 15.w,
                ),
                Row(
                  children: [
                    Text(
                      '정렬 순서',
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
                            .watch<DataManagementHomeViewModel>()
                            .sortList,
                        onTap: (index) => context
                            .read<DataManagementHomeViewModel>()
                            .onTapSort(index),
                        status: context
                            .watch<DataManagementHomeViewModel>()
                            .sortStatus),
                  ],
                ),
                SizedBox(
                  height: 30.w,
                ),
                MainButton(
                  text: '조회',
                  width: 640.w,
                  height: 70.h,
                  mode: 1,
                  onPressed: context
                          .read<DataManagementHomeViewModel>()
                          .checkedFilter()
                      ? () => context
                          .read<DataManagementHomeViewModel>()
                          .onPressedFilterSave()
                      : null,
                ),
              ],
            ),
          ),
          const Divider(),
        ],
      ),
    );
  }
}

//
//
// FilterRow 컴포넌트 : Normal
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
    return Row(
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
                color: status[index] ? Palette.editableBg : Colors.transparent,
              ),
            ),
            child: Text(
              filterList[index],
              style: TextStyle(
                color:
                    status[index] ? Palette.editableBg : Palette.waitingCardBg,
              ),
            ),
          ),
        ),
      ),
    );
  }
}

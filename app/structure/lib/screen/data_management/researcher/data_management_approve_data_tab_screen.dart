//
//
//
// 일반 데이터 승인 페이지 (Researcher)
//
//
//

import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_divider.dart';
import 'package:structure/components/custom_table_bar.dart';
import 'package:structure/components/filter_box.dart';
import 'package:structure/components/list_card.dart';
import 'package:structure/components/loading_screen.dart';
import 'package:structure/components/main_text_field.dart';
import 'package:structure/config/palette.dart';
import 'package:structure/config/usefuls.dart';
import 'package:structure/viewModel/data_management/researcher/data_management_approve_data_tab_view_model.dart';

class DataManagementApproveDataTabScreen extends StatefulWidget {
  const DataManagementApproveDataTabScreen({super.key});

  @override
  State<DataManagementApproveDataTabScreen> createState() =>
      _DataManagementApproveDataTabScreenState();
}

class _DataManagementApproveDataTabScreenState
    extends State<DataManagementApproveDataTabScreen> {
  @override
  Widget build(BuildContext context) {
    DataManagementApproveDataTabViewModel
        dataManagementApproveDataTabViewModel =
        context.watch<DataManagementApproveDataTabViewModel>();

    return GestureDetector(
      onTap: () => FocusScope.of(context).unfocus(),
      child: Scaffold(
        body: Stack(
          children: [
            SingleChildScrollView(
              scrollDirection: Axis.vertical,
              // 드래그시 키보드 닫기
              keyboardDismissBehavior: ScrollViewKeyboardDismissBehavior.onDrag,
              child: Container(
                margin: EdgeInsets.symmetric(horizontal: 40.w),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    SizedBox(height: 24.h),

                    // 필터 버튼
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        // 데이터 개수 텍스트
                        Text(
                          '${dataManagementApproveDataTabViewModel.selectedList.length}개의 데이터',
                          textAlign: TextAlign.left,
                          style: Palette.h5Secondary,
                        ),
                        // 필터 버튼
                        InkWell(
                          onTap: () => dataManagementApproveDataTabViewModel
                              .clickedFilter(context),
                          borderRadius: BorderRadius.circular(20.r),
                          child: Container(
                            padding: EdgeInsets.all(16.w),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                // 선택된 필터
                                Text(
                                  dataManagementApproveDataTabViewModel
                                      .filterdResult,
                                  style: Palette.h4,
                                ),

                                // 화살표
                                dataManagementApproveDataTabViewModel
                                        .isOpnedFilter
                                    ? const Icon(Icons.arrow_drop_up_outlined)
                                    : const Icon(Icons.arrow_drop_down),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),

                    // 필터 area
                    dataManagementApproveDataTabViewModel.isOpnedFilter
                        ? FilterBox(
                            type: 2,
                            dateList:
                                dataManagementApproveDataTabViewModel.dateList,
                            onTapDate: (index) =>
                                dataManagementApproveDataTabViewModel
                                    .onTapDate(index),
                            dateStatus: dataManagementApproveDataTabViewModel
                                .dateStatus,
                            firstDayText: dataManagementApproveDataTabViewModel
                                .firstDayText,
                            indexDay:
                                dataManagementApproveDataTabViewModel.indexDay,
                            firstDayOnTapTable: () =>
                                dataManagementApproveDataTabViewModel
                                    .onTapTable(0),
                            lastDayText: dataManagementApproveDataTabViewModel
                                .lastDayText,
                            lastDayOnTapTable: () =>
                                dataManagementApproveDataTabViewModel
                                    .onTapTable(1),
                            isOpenTable: dataManagementApproveDataTabViewModel
                                .isOpenTable,
                            focused:
                                dataManagementApproveDataTabViewModel.focused,
                            onDaySelected: (selectedDay, focusedDay) =>
                                dataManagementApproveDataTabViewModel
                                    .onDaySelected(selectedDay, focusedDay),
                            dataList:
                                dataManagementApproveDataTabViewModel.dataList,
                            onTapData: (index) =>
                                dataManagementApproveDataTabViewModel
                                    .onTapData(index),
                            dataStatus: dataManagementApproveDataTabViewModel
                                .dataStatus,
                            speciesList: dataManagementApproveDataTabViewModel
                                .speciesList,
                            onTapSpecies: (index) =>
                                dataManagementApproveDataTabViewModel
                                    .onTapSpecies(index),
                            speciesStatus: dataManagementApproveDataTabViewModel
                                .speciesStatus,
                            checkedFilter: dataManagementApproveDataTabViewModel
                                .checkedFilter(),
                            onPressedFilterSave: () =>
                                dataManagementApproveDataTabViewModel
                                    .onPressedFilterSave(),
                            statusList: dataManagementApproveDataTabViewModel
                                .statusList,
                            onTapstatus: (index) =>
                                dataManagementApproveDataTabViewModel
                                    .onTapStatus(index),
                            statusStatus: dataManagementApproveDataTabViewModel
                                .statusStatus,
                            sortList:
                                dataManagementApproveDataTabViewModel.sortList,
                            sortStatus: dataManagementApproveDataTabViewModel
                                .sortStatus,
                            onTapSort: (index) =>
                                dataManagementApproveDataTabViewModel
                                    .onTapSort(index),
                          )
                        : SizedBox(height: 16.h),

                    // 관리번호 입력 textfield
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        // 'MainTextField' 컴포넌트를 이용하여 관리 번호 검색 기능을 정의한다.
                        Expanded(
                          child: MainTextField(
                            width: double.infinity,
                            height: 80.h,
                            mainText: '관리번호 입력',
                            validateFunc: null,
                            onSaveFunc: null,
                            controller: dataManagementApproveDataTabViewModel
                                .controller,
                            focusNode:
                                dataManagementApproveDataTabViewModel.focusNode,
                            onChangeFunc: (value) =>
                                dataManagementApproveDataTabViewModel
                                    .onChanged(value),
                            hideFloatingLabel: true,
                            canAlert: true,
                            prefixIcon: const Icon(
                              Icons.search,
                              color: Colors.black,
                            ),
                            suffixIcon: dataManagementApproveDataTabViewModel
                                    .focusNode.hasFocus
                                ? IconButton(
                                    onPressed: () {
                                      dataManagementApproveDataTabViewModel
                                          .textClear(context);
                                    },
                                    icon: const Icon(
                                      Icons.cancel_outlined,
                                      color: Palette.secondary,
                                    ),
                                  )
                                : null,
                          ),
                        ),
                        SizedBox(width: 16.w),

                        // QR 코드 확인 기능을 정의한다.
                        IconButton(
                          iconSize: 48.w,
                          onPressed: () async =>
                              dataManagementApproveDataTabViewModel
                                  .clickedQr(context),
                          icon: const Icon(
                            Icons.qr_code_scanner_rounded,
                            color: Palette.primary,
                          ),
                        ),
                      ],
                    ),
                    SizedBox(height: 16.h),

                    // 육류 리스트 상단바
                    const CustomTableBar(),
                    SizedBox(height: 16.h),

                    // 육류 리스트
                    SizedBox(
                      height: 800.h,
                      child: Scrollbar(
                        thumbVisibility: true,
                        controller: dataManagementApproveDataTabViewModel
                            .scrollController,
                        child: dataManagementApproveDataTabViewModel
                                .selectedList.isEmpty
                            ? Center(
                                child: Text(
                                "데이터가 없습니다.",
                                style: Palette.h4Regular,
                              ))
                            : ListView.separated(
                                controller:
                                    dataManagementApproveDataTabViewModel
                                        .scrollController,
                                itemCount: dataManagementApproveDataTabViewModel
                                    .selectedList.length,
                                itemBuilder: (context, index) => ListCard(
                                  onTap: () async =>
                                      await dataManagementApproveDataTabViewModel
                                          .onTapApproveCard(index, context),
                                  meatId: dataManagementApproveDataTabViewModel
                                      .selectedList[index]['meatId']!,
                                  dayTime: Usefuls.parseDate(
                                      dataManagementApproveDataTabViewModel
                                          .selectedList[index]['createdAt']!),
                                  statusType:
                                      dataManagementApproveDataTabViewModel
                                          .selectedList[index]['statusType']!,
                                ),
                                keyboardDismissBehavior:
                                    ScrollViewKeyboardDismissBehavior.onDrag,
                                separatorBuilder:
                                    (BuildContext context, int index) =>
                                        const CustomDivider(),
                              ),
                      ),
                    ),
                    SizedBox(height: 40.h),
                  ],
                ),
              ),
            ),
            dataManagementApproveDataTabViewModel.isLoading
                ? const Center(child: LoadingScreen())
                : Container(),
          ],
        ),
      ),
    );
  }
}

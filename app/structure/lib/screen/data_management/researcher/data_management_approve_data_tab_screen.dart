//
//
//
// 일반 데이터 승인 페이지 (Researcher)
//
//
//

import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_divider.dart';
import 'package:structure/components/custom_table_bar_approve.dart';
import 'package:structure/components/filter_box.dart';
import 'package:structure/components/list_card_approve.dart';
import 'package:structure/components/loading_screen.dart';
import 'package:structure/components/main_text_field.dart';
import 'package:structure/config/palette.dart';
import 'package:structure/config/pallete.dart';
import 'package:structure/config/userfuls.dart';
import 'package:structure/viewModel/data_management/researcher/approve_data_view_model.dart';

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
    ApproveDataViewModel approveDataViewModel =
        context.watch<ApproveDataViewModel>();

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
                          '${approveDataViewModel.selectedList.length}개의 데이터',
                          textAlign: TextAlign.left,
                          style: Palette.h5Secondary,
                        ), // 필터 버튼
                        InkWell(
                          onTap: () =>
                              approveDataViewModel.clickedFilter(context),
                          borderRadius: BorderRadius.circular(20.r),
                          child: Container(
                            padding: EdgeInsets.all(16.w),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                // 선택된 필터
                                Text(
                                  approveDataViewModel.filterdResult,
                                  style: Pallete.h4,
                                ),

                                // 화살표
                                approveDataViewModel.isOpnedFilter
                                    ? const Icon(Icons.arrow_drop_up_outlined)
                                    : const Icon(Icons.arrow_drop_down),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),

                    // 필터 area
                    approveDataViewModel.isOpnedFilter
                        ? FilterBox(
                            type: 2,
                            dateList: approveDataViewModel.dateList,
                            onTapDate: (index) =>
                                approveDataViewModel.onTapDate(index),
                            dateStatus: approveDataViewModel.dateStatus,
                            firstDayText: approveDataViewModel.firstDayText,
                            indexDay: approveDataViewModel.indexDay,
                            firstDayOnTapTable: () =>
                                approveDataViewModel.onTapTable(0),
                            lastDayText: approveDataViewModel.lastDayText,
                            lastDayOnTapTable: () =>
                                approveDataViewModel.onTapTable(1),
                            isOpenTable: approveDataViewModel.isOpenTable,
                            focused: approveDataViewModel.focused,
                            onDaySelected: (selectedDay, focusedDay) =>
                                approveDataViewModel.onDaySelected(
                                    selectedDay, focusedDay),
                            dataList: approveDataViewModel.dataList,
                            onTapData: (index) =>
                                approveDataViewModel.onTapData(index),
                            dataStatus: approveDataViewModel.dataStatus,
                            speciesList: approveDataViewModel.speciesList,
                            onTapSpecies: (index) =>
                                approveDataViewModel.onTapSpecies(index),
                            speciesStatus: approveDataViewModel.speciesStatus,
                            checkedFilter: approveDataViewModel.checkedFilter(),
                            onPressedFilterSave: () =>
                                approveDataViewModel.onPressedFilterSave(),
                            statusList: approveDataViewModel.statusList,
                            onTapstatus: (index) =>
                                approveDataViewModel.onTapStatus(index),
                            statusStatus: approveDataViewModel.statusStatus,
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
                            validateFunc: null,
                            onSaveFunc: null,
                            controller: approveDataViewModel.controller,
                            focusNode: approveDataViewModel.focusNode,
                            onChangeFunc: (value) =>
                                approveDataViewModel.onChanged(value),
                            mainText: '관리번호 입력',
                            hideFloatingLabel: true,
                            canAlert: true,
                            prefixIcon: const Icon(
                              Icons.search,
                              color: Colors.black,
                            ),
                            suffixIcon: approveDataViewModel.focusNode.hasFocus
                                ? IconButton(
                                    onPressed: () {
                                      approveDataViewModel.textClear(context);
                                    },
                                    icon: const Icon(
                                      Icons.cancel,
                                      color: Palette.primaryContainer,
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
                              approveDataViewModel.clickedQr(context),
                          icon: const Icon(
                            Icons.qr_code_scanner_rounded,
                            color: Palette.primary,
                          ),
                        ),
                      ],
                    ),
                    SizedBox(height: 16.h),

                    // 육류 리스트 상단바
                    const CustomTableBarApprove(),
                    SizedBox(height: 16.h),

                    // 육류 리스트
                    SizedBox(
                      height: 800.h,
                      child: Scrollbar(
                        thumbVisibility: true,
                        controller: approveDataViewModel.scrollController,
                        child: ListView.separated(
                          controller: approveDataViewModel.scrollController,
                          itemCount: approveDataViewModel.selectedList.length,
                          itemBuilder: (context, index) => ListCardApprove(
                            onTap: () async => await approveDataViewModel
                                .onTapApproveCard(index, context),
                            idx: index + 1,
                            meatId: approveDataViewModel.selectedList[index]
                                ['meatId']!,
                            dayTime: Usefuls.parseDate(approveDataViewModel
                                .selectedList[index]['createdAt']!),
                            statusType: approveDataViewModel.selectedList[index]
                                ['statusType']!,
                          ),
                          keyboardDismissBehavior:
                              ScrollViewKeyboardDismissBehavior.onDrag,
                          separatorBuilder: (BuildContext context, int index) =>
                              const CustomDivider(),
                        ),
                      ),
                    ),
                    SizedBox(height: 40.h),
                  ],
                ),
              ),
            ),
            approveDataViewModel.isLoading
                ? const Center(child: LoadingScreen())
                : Container(),
          ],
        ),
      ),
    );
  }
}

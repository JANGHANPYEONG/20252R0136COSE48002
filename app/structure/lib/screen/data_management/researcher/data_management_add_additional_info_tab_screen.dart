//
//
// 추가정보 입력 페이지(View) : Researcher
//
//

import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_divider.dart';
import 'package:structure/components/filter_box.dart';
import 'package:structure/components/list_card_data_manage.dart';
import 'package:structure/components/loading_screen.dart';
import 'package:structure/components/main_text_field.dart';
import 'package:structure/config/palette.dart';
import 'package:structure/viewModel/data_management/researcher/data_management_researcher_view_model.dart';

class DataManagementAddAdditionalInfoTabScreen extends StatefulWidget {
  const DataManagementAddAdditionalInfoTabScreen({super.key});

  @override
  State<DataManagementAddAdditionalInfoTabScreen> createState() =>
      _DataManagementAddAdditionalInfoTabScreenState();
}

class _DataManagementAddAdditionalInfoTabScreenState
    extends State<DataManagementAddAdditionalInfoTabScreen> {
  @override
  Widget build(BuildContext context) {
    final DataManagementHomeResearcherViewModel
        dataManagementHomeResearcherViewModel =
        context.watch<DataManagementHomeResearcherViewModel>();

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
                          '${dataManagementHomeResearcherViewModel.selectedList.length}개의 데이터',
                          textAlign: TextAlign.left,
                          style: Palette.h5Secondary,
                        ),

                        // 필터 버튼
                        InkWell(
                          onTap: () => dataManagementHomeResearcherViewModel
                              .clickedFilter(context),
                          borderRadius: BorderRadius.circular(20.r),
                          child: Container(
                            padding: EdgeInsets.all(16.w),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                // 선택된 필터
                                Text(
                                  dataManagementHomeResearcherViewModel
                                      .filterdResult,
                                  style: Palette.h4,
                                ),

                                // 화살표
                                dataManagementHomeResearcherViewModel
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
                    dataManagementHomeResearcherViewModel.isOpnedFilter
                        ? FilterBox(
                            type: 1,
                            dateList:
                                dataManagementHomeResearcherViewModel.dateList,
                            onTapDate: (index) =>
                                dataManagementHomeResearcherViewModel
                                    .onTapDate(index),
                            dateStatus: dataManagementHomeResearcherViewModel
                                .dateStatus,
                            firstDayText: dataManagementHomeResearcherViewModel
                                .firstDayText,
                            indexDay:
                                dataManagementHomeResearcherViewModel.indexDay,
                            firstDayOnTapTable: () =>
                                dataManagementHomeResearcherViewModel
                                    .onTapTable(0),
                            lastDayText: dataManagementHomeResearcherViewModel
                                .lastDayText,
                            lastDayOnTapTable: () =>
                                dataManagementHomeResearcherViewModel
                                    .onTapTable(1),
                            isOpenTable: dataManagementHomeResearcherViewModel
                                .isOpenTable,
                            focused:
                                dataManagementHomeResearcherViewModel.focused,
                            onDaySelected: (selectedDay, focusedDay) =>
                                dataManagementHomeResearcherViewModel
                                    .onDaySelected(selectedDay, focusedDay),
                            dataList:
                                dataManagementHomeResearcherViewModel.dataList,
                            onTapData: (index) =>
                                dataManagementHomeResearcherViewModel
                                    .onTapData(index),
                            dataStatus: dataManagementHomeResearcherViewModel
                                .dataStatus,
                            speciesList: dataManagementHomeResearcherViewModel
                                .speciesList,
                            onTapSpecies: (index) =>
                                dataManagementHomeResearcherViewModel
                                    .onTapSpecies(index),
                            speciesStatus: dataManagementHomeResearcherViewModel
                                .speciesStatus,
                            checkedFilter: dataManagementHomeResearcherViewModel
                                .checkedFilter(),
                            onPressedFilterSave: () =>
                                dataManagementHomeResearcherViewModel
                                    .onPressedFilterSave(),
                            statusList: dataManagementHomeResearcherViewModel
                                .statusList,
                            onTapstatus: (index) =>
                                dataManagementHomeResearcherViewModel
                                    .onTapStatus(index),
                            statusStatus: dataManagementHomeResearcherViewModel
                                .statusStatus,
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
                            controller: dataManagementHomeResearcherViewModel
                                .controller,
                            focusNode:
                                dataManagementHomeResearcherViewModel.focusNode,
                            onChangeFunc: (value) =>
                                dataManagementHomeResearcherViewModel
                                    .onChanged(value),
                            mainText: '관리번호 입력',
                            hideFloatingLabel: true,
                            canAlert: true,
                            prefixIcon: const Icon(
                              Icons.search,
                              color: Colors.black,
                            ),
                            suffixIcon: dataManagementHomeResearcherViewModel
                                    .focusNode.hasFocus
                                ? IconButton(
                                    onPressed: () {
                                      dataManagementHomeResearcherViewModel
                                          .textClear(context);
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
                              dataManagementHomeResearcherViewModel
                                  .clickedQr(context),
                          icon: const Icon(
                            Icons.qr_code_scanner_rounded,
                            color: Palette.primary,
                          ),
                        ),
                      ],
                    ),
                    SizedBox(height: 16.h),

                    // 육류 리스트
                    SizedBox(
                      height: 800.h,
                      child: Scrollbar(
                        thumbVisibility: true,
                        controller: dataManagementHomeResearcherViewModel
                            .scrollController,
                        child: ListView.separated(
                          controller: dataManagementHomeResearcherViewModel
                              .scrollController,
                          itemCount: dataManagementHomeResearcherViewModel
                              .selectedList.length,
                          itemBuilder: (context, index) => ListCardDataManage(
                            onTap: () async =>
                                await dataManagementHomeResearcherViewModel
                                    .onTap(index, context),
                            idx: index + 1,
                            meatId: dataManagementHomeResearcherViewModel
                                .selectedList[index]['meatId']!,
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
            dataManagementHomeResearcherViewModel.isLoading
                ? const Center(child: LoadingScreen())
                : Container(),
          ],
        ),
      ),
    );
  }
}

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
import 'package:structure/viewModel/data_management/researcher/data_management_add_additional_info_tab_view_model.dart';

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
    final DataManagementAddAdditionalInfoTabViewModel
        dataManagementAddAdditionalInfoTabViewModel =
        context.watch<DataManagementAddAdditionalInfoTabViewModel>();

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
                        Text(
                          '${dataManagementAddAdditionalInfoTabViewModel.selectedList.length}개의 데이터',
                          textAlign: TextAlign.left,
                          style: Palette.h5Secondary,
                        ),

                        // 필터 버튼
                        InkWell(
                          onTap: () =>
                              dataManagementAddAdditionalInfoTabViewModel
                                  .clickedFilter(),
                          borderRadius: BorderRadius.circular(20.r),
                          child: Container(
                            padding: EdgeInsets.all(16.w),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                // 선택된 필터
                                Text(
                                  dataManagementAddAdditionalInfoTabViewModel
                                      .filterdResult,
                                  style: Palette.h4,
                                ),

                                // 화살표
                                dataManagementAddAdditionalInfoTabViewModel
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
                    dataManagementAddAdditionalInfoTabViewModel.isOpnedFilter
                        ? FilterBox(
                            type: 1,
                            dateList:
                                dataManagementAddAdditionalInfoTabViewModel
                                    .dateList,
                            onTapDate: (index) =>
                                dataManagementAddAdditionalInfoTabViewModel
                                    .onTapDate(index),
                            dateStatus:
                                dataManagementAddAdditionalInfoTabViewModel
                                    .dateStatus,
                            firstDayText:
                                dataManagementAddAdditionalInfoTabViewModel
                                    .firstDayText,
                            indexDay:
                                dataManagementAddAdditionalInfoTabViewModel
                                    .indexDay,
                            firstDayOnTapTable: () =>
                                dataManagementAddAdditionalInfoTabViewModel
                                    .onTapTable(0),
                            lastDayText:
                                dataManagementAddAdditionalInfoTabViewModel
                                    .lastDayText,
                            lastDayOnTapTable: () =>
                                dataManagementAddAdditionalInfoTabViewModel
                                    .onTapTable(1),
                            isOpenTable:
                                dataManagementAddAdditionalInfoTabViewModel
                                    .isOpenTable,
                            focused: dataManagementAddAdditionalInfoTabViewModel
                                .focused,
                            onDaySelected: (selectedDay, focusedDay) =>
                                dataManagementAddAdditionalInfoTabViewModel
                                    .onDaySelected(selectedDay, focusedDay),
                            dataList:
                                dataManagementAddAdditionalInfoTabViewModel
                                    .dataList,
                            onTapData: (index) =>
                                dataManagementAddAdditionalInfoTabViewModel
                                    .onTapData(index),
                            dataStatus:
                                dataManagementAddAdditionalInfoTabViewModel
                                    .dataStatus,
                            speciesList:
                                dataManagementAddAdditionalInfoTabViewModel
                                    .speciesList,
                            onTapSpecies: (index) =>
                                dataManagementAddAdditionalInfoTabViewModel
                                    .onTapSpecies(index),
                            speciesStatus:
                                dataManagementAddAdditionalInfoTabViewModel
                                    .speciesStatus,
                            checkedFilter:
                                dataManagementAddAdditionalInfoTabViewModel
                                    .checkedFilter(),
                            onPressedFilterSave: () =>
                                dataManagementAddAdditionalInfoTabViewModel
                                    .onPressedFilterSave(),
                            statusList:
                                dataManagementAddAdditionalInfoTabViewModel
                                    .statusList,
                            onTapstatus: (index) =>
                                dataManagementAddAdditionalInfoTabViewModel
                                    .onTapStatus(index),
                            statusStatus:
                                dataManagementAddAdditionalInfoTabViewModel
                                    .statusStatus,
                            sortList:
                                dataManagementAddAdditionalInfoTabViewModel
                                    .sortList,
                            onTapSort: (index) =>
                                dataManagementAddAdditionalInfoTabViewModel
                                    .onTapSort(index),
                            sortStatus:
                                dataManagementAddAdditionalInfoTabViewModel
                                    .sortStatus,
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
                            controller:
                                dataManagementAddAdditionalInfoTabViewModel
                                    .controller,
                            focusNode:
                                dataManagementAddAdditionalInfoTabViewModel
                                    .focusNode,
                            onChangeFunc: (value) =>
                                dataManagementAddAdditionalInfoTabViewModel
                                    .onChanged(value),
                            hideFloatingLabel: true,
                            canAlert: true,
                            prefixIcon: const Icon(
                              Icons.search,
                              color: Colors.black,
                            ),
                            suffixIcon:
                                dataManagementAddAdditionalInfoTabViewModel
                                        .focusNode.hasFocus
                                    ? IconButton(
                                        onPressed: () {
                                          dataManagementAddAdditionalInfoTabViewModel
                                              .textClear();
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
                              dataManagementAddAdditionalInfoTabViewModel
                                  .clickedQr(),
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
                        controller: dataManagementAddAdditionalInfoTabViewModel
                            .scrollController,
                        child: dataManagementAddAdditionalInfoTabViewModel
                                .selectedList.isEmpty
                            ? Center(
                                child: Text(
                                "데이터가 없습니다.",
                                style: Palette.h4Regular,
                              ))
                            : ListView.separated(
                                controller:
                                    dataManagementAddAdditionalInfoTabViewModel
                                        .scrollController,
                                itemCount:
                                    dataManagementAddAdditionalInfoTabViewModel
                                        .selectedList.length,
                                itemBuilder: (context, index) =>
                                    ListCardDataManage(
                                  onTap: () async =>
                                      await dataManagementAddAdditionalInfoTabViewModel
                                          .onTap(index),
                                  idx: index + 1,
                                  meatId:
                                      dataManagementAddAdditionalInfoTabViewModel
                                          .selectedList[index]['meatId']!,
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
            dataManagementAddAdditionalInfoTabViewModel.isLoading
                ? const Center(child: LoadingScreen())
                : Container(),
          ],
        ),
      ),
    );
  }
}

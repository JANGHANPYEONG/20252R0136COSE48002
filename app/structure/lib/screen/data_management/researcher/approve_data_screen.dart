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
import 'package:structure/components/custom_table_bar_approve.dart';
import 'package:structure/components/filter_box.dart';
import 'package:structure/components/list_card_approve.dart';
import 'package:structure/components/loading_screen.dart';
import 'package:structure/components/main_text_field.dart';
import 'package:structure/config/pallete.dart';
import 'package:structure/config/userfuls.dart';
import 'package:structure/viewModel/data_management/researcher/approve_data_view_model.dart';

class ApproveDataScreen extends StatefulWidget {
  const ApproveDataScreen({super.key});

  @override
  State<ApproveDataScreen> createState() => _ApproveDataScreenState();
}

class _ApproveDataScreenState extends State<ApproveDataScreen> {
  @override
  Widget build(BuildContext context) {
    ApproveDataViewModel approveDataViewModel =
        context.watch<ApproveDataViewModel>();

    return GestureDetector(
      onTap: () => FocusScope.of(context).unfocus(),
      child: Scaffold(
        backgroundColor: Colors.white,
        body: Stack(
          children: [
            SingleChildScrollView(
              scrollDirection: Axis.vertical,
              // 드래그시 키보드 닫기
              keyboardDismissBehavior: ScrollViewKeyboardDismissBehavior.onDrag,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.center,
                mainAxisSize: MainAxisSize.min,
                children: [
                  SizedBox(height: 16.h),

                  // 필터 버튼
                  Container(
                    margin: EdgeInsets.symmetric(horizontal: 40.w),
                    alignment: Alignment.centerRight,
                    child: InkWell(
                      onTap: () => approveDataViewModel.clickedFilter(context),
                      borderRadius: BorderRadius.circular(20.r),
                      child: Container(
                        padding: EdgeInsets.all(8.w),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            // 선택된 필터
                            Text(
                              approveDataViewModel.filterdResult,
                              style: Palette.h4,
                            ),

                            // 화살표
                            approveDataViewModel.isOpnedFilter
                                ? const Icon(Icons.arrow_drop_up_outlined)
                                : const Icon(Icons.arrow_drop_down),
                          ],
                        ),
                      ),
                    ),
                  ),

                  // 필터 area
                  approveDataViewModel.isOpnedFilter
                      ? FilterBox(
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
                        )
                      : SizedBox(height: 16.h),

                  // 관리번호 입력 textfield
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      // 'MainTextField' 컴포넌트를 이용하여 관리 번호 검색 기능을 정의한다.
                      MainTextField(
                        validateFunc: null,
                        onSaveFunc: null,
                        controller: approveDataViewModel.controller,
                        focusNode: approveDataViewModel.focusNode,
                        onChangeFunc: (value) =>
                            approveDataViewModel.onChanged(value),
                        mainText: '관리번호 입력',
                        hideFloatingLabel: true,
                        width: 560.w,
                        height: 72.h,
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
                                  color: Palette.meatRegiCardBg,
                                ),
                              )
                            : null,
                      ),
                      IconButton(
                        // QR 코드 확인 기능을 정의한다.
                        iconSize: 48.w,
                        onPressed: () async =>
                            approveDataViewModel.clickedQr(context),
                        icon: const Icon(
                          Icons.qr_code_scanner_rounded,
                          color: Palette.meatRegiBtnBg,
                        ),
                      ),
                    ],
                  ),
                  SizedBox(height: 24.h),

                  // 육류 리스트 상단바
                  const CustomTableBarApprove(),
                  SizedBox(height: 16.h),

                  // 육류 리스트
                  Container(
                    margin: EdgeInsets.symmetric(horizontal: 40.w),
                    height: 800.h,
                    child: ListView.separated(
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
                  SizedBox(height: 50.h),
                ],
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
